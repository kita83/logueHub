import os
from io import BytesIO
import uuid
import logging
from time import mktime
from datetime import datetime
import requests
import feedparser
import pytz
import boto3
from django.core.files.storage import default_storage
from django.utils import timezone
from django.utils import html
from PIL import Image
from logue import settings
from . import models


logger = logging.getLogger(__name__)


def delete_previous_file(function):
    """
    不要となる古いファイルを削除する為のデコレータ実装.

    :param function: メイン関数
    :return: wrapper
    """
    def wrapper(*args, **kwargs):
        """Wrapper 関数.

        :param args: 任意の引数
        :param kwargs: 任意のキーワード引数
        :return: メイン関数実行結果
        """
        self = args[0]

        # 保存前のファイル名を取得
        result = models.Channel.objects.filter(pk=self.pk)
        previous = result[0] if len(result) else None
        super(models.Channel, self).save()

        # 関数実行
        result = function(*args, **kwargs)

        # 保存前のファイルがあったら削除
        if previous:
            os.remove(settings.MEDIA_ROOT + '/' + previous.cover_image.name)
        return result
    return wrapper


def save_image(image_url, db_channel):
    """画像を保存する.

    Arguments:
        image_url -- 画像取得URL
        db_channel -- チャンネル

    Returns:
        rel_path -- DB登録用パス
    """
    res = requests.get(image_url)
    if res.status_code != 200:
        return ''

    # 保存する画像名を取得
    filename = image_url.split('/')[-1]
    unique_name = get_image_name(filename)

    # 画像ファイル書き込み用パス
    if settings.DEBUG:
        prefix = settings.MEDIA_ROOT + '/images/'
    else:
        prefix = settings.MEDIA_URL + 'images/'
    path = prefix + unique_name

    # DB登録用パス
    rel_path = 'images/' + unique_name

    # 以前の画像を削除する
    if db_channel.cover_image:
        if settings.DEBUG:
            old_path = settings.MEDIA_ROOT + '/' + db_channel.cover_image.name
        else:
            old_path = settings.MEDIA_URL + db_channel.cover_image.name
        if os.path.exists(old_path):
            os.remove(old_path)

    with default_storage.open(rel_path, 'wb') as file:
        file.write(res.content)

    return rel_path


def get_image_name(filename):
    """
    カスタマイズした画像パスを取得する.

    :param filename: 元ファイル名
    :return: カスタマイズしたファイル名を含む画像パス
    """
    # UUIDで一意な名前にする
    name = str(uuid.uuid4()).replace('-', '')
    # 拡張子
    extension = os.path.splitext(filename)[-1]
    # 末尾にパラメータを含む場合、除外する
    if '?' in extension:
        splited = extension.split('?')
        extension = splited[0]
    return name + extension


def get_feed(feed_url):
    """新規にフィードを取得し、登録する.

    Arguments:
        db_channel -- Channelモデルインスタンス
    Return:
        result(str) -- 処理成功の場合 'success' を返す
    """
    # リクエストURLをもとにパース処理
    parsed = feedparser.parse(feed_url)
    # 取得フィードステータス確認
    is_valid_feed = check_feed_status(parsed, feed_url)
    # ステータス異常があれば、処理終了
    if not is_valid_feed:
        return ''

    # チャンネルデータを先に登録する。既に登録があれば既存データを取得する
    stored_channel, created = models.Channel.objects.get_or_create(
        feed_url=feed_url)

    # チャンネルデータ更新
    save_channel(parsed, stored_channel)
    # エピソード登録
    save_episodes(parsed, stored_channel)

    return 'success'

def check_feed_status(parsed, feed_url):
    """取得フィードの状態をチェックする.

    Arguments:
        parsed(json) -- パース済 Json データ
        feed_url(str) -- リクエストFeed URL
    Return:
        result(boolean) -- ステータス異常なし: True
    """
    # パース成否確認
    if hasattr(parsed.feed, 'bozo_exception'):
        msg = 'logue get_feeds found Malformed feed, "%s": %s'\
            % (feed_url, parsed.feed.bozo_exception)
        logger.warning(msg)
        return False

    # タイトル、リンクの属性存在確認
    for attr in ['title', 'title_detail']:
        # 属性がない場合、エラー
        if not hasattr(parsed.feed, attr):
            msg = 'Channel "%s" has no %s' % (feed_url, attr)
            logger.error(msg)
            return False

    # 音声ファイルURL有無チェック
    entry = parsed.entries[0]
    is_audiofeed = False
    if hasattr(entry, 'links'):
        for link in entry.links:
            if hasattr(link, 'type') and link.type == 'audio/mpeg':
                is_audiofeed = True

    if not is_audiofeed:
        msg = 'Channel "%s" has no audio link' % (feed_url)
        logger.error(msg)
        return False

    return True


def save_channel(parsed, stored_channel):
    """チャンネルデータを登録・更新する.

    Arguments:
        parsed(json) -- パース済 Json データ
        stored_channel(quryset) -- Channelモデルインスタンス
    Return:
    """
    # タイトル取得
    if parsed.feed.title_detail.type == 'text/plain':
        # 'text/plain' の場合、htmlエスケープ処理する
        stored_channel.title = html.escape(parsed.feed.title)
    else:
        stored_channel.title = parsed.feed.title

    # link取得
    stored_channel.link = parsed.feed.link

    # author取得
    if hasattr(parsed.feed, 'author'):
        stored_channel.author = parsed.feed.author
    else:
        stored_channel.author = ''

    # チャンネル説明取得
    if hasattr(parsed.feed, 'description_detail')\
            and hasattr(parsed.feed, 'description'):
        # 'text/plain'の場合、htmlエスケープ処理する
        if parsed.feed.description_detail.type == 'text/plain':
            stored_channel.description = html.escape(parsed.feed.description)
        else:
            stored_channel.description = parsed.feed.description
    else:
        stored_channel.description = ''

    # 最終取得日
    stored_channel.last_polled_time = timezone.now()

    # 画像
    if hasattr(parsed.feed, 'image'):
        # ストレージにイメージ画像を保存
        image_url = parsed.feed.image.href
        path = save_image(image_url, stored_channel)
        stored_channel.cover_image = path

        stored_channel.width_field = '400'
        stored_channel.height_field = '400'

        # img = Image.open(settings.MEDIA_URL + '/' + path)
        # img.thumbnail((400, 400), Image.ANTIALIAS)
        # img.save(settings.MEDIA_URL + '/' + path)

    # データ更新
    stored_channel.save()

def save_episodes(parsed, stored_channel):
    """エピソードを登録する.

    Arguments:
        parsed(json) -- パース済 Json データ
        stored_channel(quryset) -- Channelモデルインスタンス
    Return:
    """
    # エピソード登録処理
    for i, entry in enumerate(parsed.entries):
        # 属性存在判定フラグ
        missing_attr = False
        for attr in ['title', 'title_detail', 'description']:
            if not hasattr(entry, attr):
                msg = 'logue get_feeds. Episode has no %s' % (attr)
                logger.error(msg)
                missing_attr = True

        if missing_attr:
            continue

        # タイトル
        if entry.title == '':
            msg = 'logue get_feeds. Entry "%s" has a blank title'\
                % (entry.title)
            logger.warning(msg)
            continue

        # 音声ファイルURL
        audio_url = None
        if hasattr(entry, 'links'):
            for link in entry.links:
                if hasattr(link, 'type') and link.type == 'audio/mpeg':
                    audio_url = link.href

        if not audio_url:
            msg = 'logue get_feeds. Episode %s in %s has a no audio URL'\
                % (entry.title, stored_channel.title)
            logger.warning(msg)
            continue

        db_entry, created = models.Episode.objects.get_or_create(
            channel=stored_channel, audio_url=audio_url)

        # エピソードが初回登録の場合、発行日時、タイトル、説明を追加する
        if created:
            # 発行日時
            published_time = ''
            # 日付データに変換する
            if hasattr(entry, 'published_parsed'):
                if entry.published_parsed is None:
                    published_time = timezone.now()
                else:
                    published_time = datetime.fromtimestamp(
                        mktime(entry.published_parsed))
                    try:
                        published_time = pytz.timezone(
                            settings.TIME_ZONE).localize(published_time, is_dst=None)
                    except pytz.exceptions.AmbiguousTimeError:
                        pytz_timezone = pytz.timezone(settings.TIME_ZONE)
                        published_time = pytz_timezone.localize(
                            published_time, is_dst=False)
                    now = timezone.now()
                    if published_time > now:
                        published_time = now
            # 発行日時
            db_entry.published_time = published_time

            # タイトル: 'text/plain'の場合、htmlエスケープする
            if entry.title_detail.type == 'text/plain':
                db_entry.title = html.escape(entry.title)
            else:
                db_entry.title = entry.title

            # リンク
            if hasattr(entry, 'link'):
                db_entry.link = entry.link
            else:
                db_entry.link = ''

            # 収録時間
            if hasattr(entry, 'itunes_duration'):
                db_entry.duration = entry.itunes_duration
            else:
                db_entry.duration = ''

            # エピソード説明: 'text/plain'の場合、htmlエスケープする
            if hasattr(entry, 'description_detail')\
                    and entry.description_detail.type != 'text/plain':
                db_entry.description = entry.description
            else:
                db_entry.description = html.escape(entry.description)

            # エピソード保存
            db_entry.save()
