import requests
import feedparser
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.views import View
from django.views import generic
from django.http import JsonResponse
from .forms import SubscriptionForm
from .models import Channel, Episode, Like
from . import utils


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
        exist_ch = utils.get_exist_channel(feed_url)

        # チャンネル未登録の場合、先に新規登録する
        if not exist_ch:
            new_registration(feed_url, user)
            exist_ch = utils.get_exist_channel(feed_url)

        # 最新エピソードを取得
        exist_ep = utils.get_exist_epsode(exist_ch[0])

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


class EpisodeDetailView(generic.DetailView):
    """
    エピソード詳細画面
    """
    model = Episode
    template_name = 'feed/ep_detail.html'

    def get_context_data(self, *args, **kwargs):
        """エピソードが Like されている場合は Like データを渡す"""
        context = super().get_context_data(*args, **kwargs)
        user = self.request.user
        # TODO: フィルタリングがうまくできているかテストする
        context['like'] = Like.objects.filter(episode=context['episode'], user=user)
        return context


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
        utils.save_channel(ch, feed_url)

        c = Channel.objects.filter(feed_url=feed_url)
        exist_ch = c[0]

        # 最新エピソード登録
        utils.save_episode(exist_ch, entries)

        # 購読情報登録
        utils.save_subscription(exist_ch, user)


def api_v1_posts(request):
    """Likeされたエピソードの登録処理をする"""
    if request.method == 'POST':
        ep_id = request.POST.get('ep_id')
        episode = Episode.objects.get(id=ep_id)
        user = request.user
        
        if len(episode) == 0:
            return None

        episode = utils.save_like(episode, user)
        d = {
            'result': episode
        }
        return JsonResponse(d)
