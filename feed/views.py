import requests
import feedparser
import datetime
from django.shortcuts import render
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


class ChannelDetailView(View):
    """
    チャンネル詳細画面
    指定された登録チャンネルの最新エピソードを表示する
    """
    template_name = 'feed/ch_detail.html'

    def get(self, request):
        new = []
        tmp = {
            'title': 'ep0001',
            'author': 'chris',
            'release_date': '2017年12月30日'
        }
        new.append(tmp)
        context = {
            'forms': new
        }
        return render(request, self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        """フィード登録項目に入力がある場合、チャンネル登録処理をする"""
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

            return render(request, self.template_name, {'forms': forms})

        return render(request, 'feed/index.html')


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


class ChannelCreateView(generic.CreateView):
    model = Episode
    form_class = SubscriptionForm

    def form_valid(self, form):
        pass

    def form_invalid(self, form):
        pass


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

    title = ch.title
    author = ch.author
    description = ch.summary
    link = ch.link
    feed_url = feed_url
    cover_image = ch.image.href

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
        title = entry.title
        link = entry.link
        description = entry.description
        d = datetime.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %z')
        release_date = d
        duration = entry.itunes_duration

        Episode.objects.create(
            channel=ch,
            title=title,
            link=link,
            description=description,
            release_date=release_date,
            duration=duration
        )
