import os
import datetime
import uuid
import requests
import feedparser
import pytz
import dateutil.parser
from time import mktime

from django.utils import timezone
from django.utils import html
from logue import settings
from . import models

import logging

logger = logging.getLogger(__name__)


def get_exist_channel(require_url):
    """
    登録済みのチャンネルデータを返す
    存在しない場合: None
    """
    try:
        ch = models.Channel.objects.filter(feed_url=require_url)
    except models.Channel.DoesNotExist:
        pass

    return ch


def get_exist_epsode(require_ch):
    """
    登録済みのエピソードデータを返す
    存在しない場合: None
    """
    rtn = models.Episode.objects.filter(channel=require_ch)
    if not rtn:
        return None
    return rtn


def save_channel(ch, feed_url):
    """
    feedデータを Channel に登録する
    """
    if ch is None:
        return None

    title = ch.title if hasattr(ch, 'title') else ''
    author = ch.author if hasattr(ch, 'author') else ''
    description = ch.summary if hasattr(ch, 'summary') else ''
    link = ch.link if hasattr(ch, 'link') else ''
    feed_url = feed_url
    cover_image = ''

    if hasattr(ch, 'image'):
        path = ch.image.href
        cover_image = save_image(path)

    models.Channel.objects.create(
        title=title,
        description=description,
        link=link,
        feed_url=feed_url,
        author_name=author,
        cover_image=cover_image,
        width_field=200,
        height_field=200
    )


def save_episode(ch, entries):
    """
    feedデータを Episode に登録する
    """
    for entry in entries:
        title = entry.title if hasattr(entry, 'title') else ''
        link = entry.link if hasattr(entry, 'link') else ''
        audio_url = entry.links[0].href if hasattr(entry, 'links') else ''
        description = entry.description if hasattr(entry, 'description') else ''
        duration = entry.itunes_duration if hasattr(entry, 'duration') else ''
        release_date = ''

        if hasattr(entry, 'published'):
            # 日付データに変換する
            d = dateutil.parser.parse(entry.published)
            release_date = d

        models.Episode.objects.create(
            channel=ch,
            title=title,
            link=link,
            audio_url=audio_url,
            description=description,
            release_date=release_date,
            duration=duration
        )


def save_subscription(ch, user):
    """
    アカウントとチャンネルの関連を Subscription に登録する
    """
    models.Subscription.objects.create(
        channel=ch,
        user=user
    )


def save_like(episode, user):
    """
    Like情報を登録する
    """
    models.Like.objects.create(
        episode=episode,
        user=user
    )


def delete_like(episode, user):
    """
    Like情報を削除する
    """
    models.Like.objects.filter(
        episode=episode,
        user=user
    ).delete()


def delete_previous_file(function):
    """不要となる古いファイルを削除する為のデコレータ実装.

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
            os.remove(settings.MEDIA_ROOT + '/' + previous.image.name)
        return result
    return wrapper


def save_image(image_url):
    """
    画像を保存する.

    :param image_url: 画像取得URL
    :return: DB登録用パス
    """
    res = requests.get(image_url)

    if res.status_code != 200:
        return ''

    # 保存する画像名を取得
    filename = image_url.split("/")[-1]
    unique_name = get_image_name(filename)

    # 画像ファイル書き込み用パス
    prefix = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/media/images/'
    path = prefix + unique_name

    # DB登録用パス
    rel_prefix = 'images/'
    rel_path = rel_prefix + unique_name

    with open(path, 'wb') as file:
        file.write(res.content)
    return rel_path


def get_image_name(filename):
    """カスタマイズした画像パスを取得する.

    :param filename: 元ファイル名
    :return: カスタマイズしたファイル名を含む画像パス
    """
    # UUIDで一意な名前にする
    name = str(uuid.uuid4()).replace('-', '')
    # 拡張子
    extension = os.path.splitext(filename)[-1]
    return name + extension


def poll_feed(db_channel):
    """
    Read through a feed looking for new entries.

    :param db_channel: Channelモデルインスタンス
    """
    parsed = feedparser.parse(db_channel.feed_url)

    # パース失敗の場合、処理終了
    if hasattr(parsed.feed, 'bozo_exception'):
        msg = 'logue poll_feeds found Malformed feed, "%s": %s'\
            % (db_channel.xml_url, parsed.feed.bozo_exception)
        logger.warning(msg)
        print(msg)
        return

    # 発行日時
    if hasattr(parsed.feed, 'published_parsed'):
        if parsed.feed.published_parsed is None:
            published_time = timezone.now()
        else:
            published_time = datetime.fromtimestamp(
                mktime(parsed.feed.published_parsed)
            )
        try:
            published_time = pytz.timezone(
                settings.TIME_ZONE).localize(published_time, is_dst=None)
        except pytz.exceptions.AmbiguousTimeError:
            pytz_timezone = pytz.timezone(settings.TIME_ZONE)
            published_time = pytz_timezone.localize(
                published_time, is_dst=False)
        if db_channel.published_time\
                and db_channel.published_time >= published_time:
            return

        db_channel.published_time = published_time

    # タイトル、リンクの属性存在確認
    for attr in ['title', 'title_detail', 'link']:
        # 属性がない場合、エラー
        if not hasattr(parsed.feed, attr):
            msg = 'Feedreader poll_feeds. Feed "%s" has no %s'\
                % (db_channel.feed_url, attr)
            logger.error(msg)
            print(msg)
            return

    # タイトル: 'text/plain'の場合、htmlエスケープする
    if parsed.feed.title_detail.type == 'text/plain':
        db_channel.title = html.escape(parsed.feed.title)
    else:
        db_channel.title = parsed.feed.title

    # リンク
    db_channel.link = parsed.feed.link

    # author
    if hasattr(parsed.feed, 'author'):
        db_channel.author = parsed.feed.author
    else:
        db_channel.author = ''

    if hasattr(parsed.feed, 'description_detail')\
            and hasattr(parsed.feed, 'description'):
        # チャンネル説明: 'text/plain'の場合、htmlエスケープする
        if parsed.feed.description_detail.type == 'text/plain':
            db_channel.description = html.escape(parsed.feed.description)
        else:
            db_channel.description = parsed.feed.description
    else:
        db_channel.description = ''

    # 最終取得日
    db_channel.last_polled_time = timezone.now()

    # 画像
    if hasattr(parsed.feed, 'image'):
        # ストレージにイメージ画像を保存
        image_url = parsed.feed.image.href
        path = save_image(image_url)
        # 画像が取得できた場合、以前の画像を削除する
        if path and db_channel.image != '':
            os.remove(settings.MEDIA_ROOT + '/' + db_channel.image.name)
        db_channel.image = path

    # チャンネル保存
    db_channel.save()

    print('%d entries to process in %s' % (
        len(parsed.entries), db_channel.title))

    for i, entry in enumerate(parsed.entries):
        # 属性存在判定フラグ
        missing_attr = False
        for attr in ['title', 'title_detail', 'link', 'description']:
            if not hasattr(entry, attr):
                msg = 'Feedreader poll_feeds. Entry "%s" has no %s'\
                    % (entry.link, attr)
                logger.error(msg)
                print(msg)
                missing_attr = True

        if missing_attr:
            continue

        if entry.title == "":
            msg = 'Feedreader poll_feeds. Entry "%s" has a blank title'\
                % (entry.link)
            print(msg)
            logger.warning(msg)
            continue

        db_entry, created = models.Episode.objects.get_or_create(
            channel=db_channel, link=entry.link)

        # エピソードが初回登録の場合、発行日時、タイトル、説明を追加する
        if created:
            if hasattr(entry, 'published_parsed'):
                if entry.published_parsed is None:
                    published_time = timezone.now()
                else:
                    published_time = datetime.fromtimestamp(
                        mktime(entry.published_parsed))
                    try:
                        published_time = pytz.timezone(
                                settings.TIME_ZONE
                            ).localize(published_time, is_dst=None)
                    except pytz.exceptions.AmbiguousTimeError:
                        pytz_timezone = pytz.timezone(settings.TIME_ZONE)
                        published_time = pytz_timezone.localize(
                            published_time, is_dst=False)

                    # 未来日付の場合、現在日時を入れる
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

            # 収録時間
            if hasattr(entry, 'itunes_duration'):
                db_channel.duration = entry.itunes_duration
            else:
                db_channel.duration = ''

            # 音声ファイルURL
            if hasattr(entry, 'links'):
                for link in entry.links:
                    if hasattr(link, 'type') and link.type == 'audio/mpeg':
                        db_channel.audio_url = link.href
            else:
                db_channel.audio_url = ''

            # Lots of entries are missing descrtion_detail attributes.
            # Escape their content by default.
            if hasattr(entry, 'description_detail')\
                    and entry.description_detail.type != 'text/plain':
                db_entry.description = entry.description
            else:
                # エピソード説明: 'text/plain'の場合、htmlエスケープする
                db_entry.description = html.escape(entry.description)

            # エピソード保存
            db_entry.save()
