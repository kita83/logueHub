import os
import datetime
import uuid
import requests
from logue import settings
from . import models


def get_exist_channel(require_url):
    """
    登録済みのチャンネルデータを返す
    存在しない場合: None
    """
    rtn = models.Channel.objects.filter(feed_url=require_url)
    if not rtn:
        return None
    return rtn


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
        description = entry.description if hasattr(entry, 'description') else ''
        duration = entry.itunes_duration if hasattr(entry, 'duration') else ''
        release_date = ''

        if hasattr(entry, 'published'):
            d = datetime.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
            release_date = d

        models.Episode.objects.create(
            channel=ch,
            title=title,
            link=link,
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


def save_like(episode):
    """
    Like情報を登録する
    """
    pass
    # models.Like.objects.create(
    #     channel=ch,
    #     user=user
    # )


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


def save_image(url, name=None):
    """
    画像を保存する
    """
    res = requests.get(url)

    if res.status_code != 200:
        return ''

    # 保存する画像名を取得
    filename = url.split("/")[-1]
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
