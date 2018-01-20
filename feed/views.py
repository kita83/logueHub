import os
import requests
import feedparser
import datetime
import uuid
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views import View
from django.views import generic
from .forms import SubscriptionForm
from .models import Channel, Episode, Subscription


class IndexView(View):
    template_name = 'feed/index.html'

    def get(self, request):
        form = SubscriptionForm()
        # ジャンル"Software How-To"のPodcastランキング情報を取得
        url = 'https://itunes.apple.com/jp/rss/topaudiopodcasts/genre=1480/json'
        res = requests.get(url).json()

        # 表示用データ抽出
        feeds = []
        for feed in res['feed']['entry']:
            # エピソードタイトル
            title = 'episode title'
            # チャンネルタイトル
            channel = feed['im:name']['label']
            # 収録者
            author = feed['im:artist']['label']
            # リリース日
            release_date = feed['im:releaseDate']['attributes']['label']
            tmp = {
                'title': title,
                'channel': channel,
                'author': author,
                'release_date': release_date
            }
            feeds.append(tmp)

        return render(request, self.template_name, {
            'feeds': feeds,
            'form': form
        })


@require_POST
def entry(request):
    """
    下記モデルにリクエストFeedを新規登録する
    Subscription

    既存データがなければ下記も併せて登録する
    Channel, Episode, Tag
    """
    form = SubscriptionForm(request.POST)
    user = request.user

    if form.is_valid():
        feed_url = form.cleaned_data['require_url']

        # DBから登録済みデータを取得
        exist_ch = get_exist_channel(feed_url)

        # チャンネル未登録の場合、先に新規登録する
        if not exist_ch:
            new_registration(feed_url, user)
            exist_ch = get_exist_channel(feed_url)

        # 最新エピソードを取得
        exist_ep = get_exist_epsode(exist_ch[0])

        forms = []
        if exist_ep:
            for ep in exist_ep:
                form = {
                    'title': ep.title,
                    'link': ep.link,
                    'description': ep.description,
                    'release_date': ep.release_date,
                    'duration': ep.duration
                }
                forms.append(form)

        return render(request, 'feed/ch_detail.html', context={'channel': exist_ch[0]})

    return render(request, 'feed/index.html')


class ChannelDetailView(generic.DetailView):
    """
    チャンネル詳細画面
    指定された登録チャンネルの最新エピソードを表示する
    """
    model = Channel
    template_name = 'feed/ch_detail.html'


class EpisodeAllView(generic.TemplateView):
    """
    全チャンネルの未聴エピソードを表示
    """
    template_name = 'feed/ep_all.html'


class LikeListView(generic.TemplateView):
    """
    Likeされた全エピソードリストを表示
    """
    template_name = 'feed/like_list.html'


class SettingsView(generic.TemplateView):
    """
    各種設定項目を表示
    """
    template_name = 'feed/settings.html'


def get_exist_channel(require_url):
    """
    登録済みのチャンネルデータを返す
    存在しない場合: None
    """
    rtn = Channel.objects.filter(feed_url=require_url)
    if not rtn:
        return None
    return rtn


def get_exist_epsode(require_ch):
    """
    登録済みのエピソードデータを返す
    存在しない場合: None
    """
    rtn = Episode.objects.filter(channel=require_ch)
    if not rtn:
        return None
    return rtn


def new_registration(feed_url, user):
    """
    新規カテゴリ、チャンネル、最新エピソードを登録する
    """
    feeds = feedparser.parse(feed_url)
    if feeds:
        # チャンネル
        ch = feeds.channel
        # エピソード
        entries = feeds.entries

        # チャンネル新規登録
        save_channel(ch, feed_url)

        c = Channel.objects.filter(feed_url=feed_url)
        exist_ch = c[0]

        # 最新エピソード登録
        save_episode(exist_ch, entries)

        # 購読情報登録
        save_Subscription(exist_ch, user)


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

    print(cover_image)

    Channel.objects.create(
        title=title,
        description=description,
        link=link,
        feed_url=feed_url,
        author_name=author,
        cover_image=cover_image
    )


def save_Subscription(ch, user):
    """
    アカウントとチャンネルの関連を Subscription に登録する
    """
    Subscription.objects.create(
        channel=ch,
        user=user
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

        Episode.objects.create(
            channel=ch,
            title=title,
            link=link,
            description=description,
            release_date=release_date,
            duration=duration
        )


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
