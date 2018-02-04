import datetime
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views import generic
from django.http import JsonResponse
from django.db.models import Count
from .forms import SubscriptionForm
from .models import Channel, Episode, Like
from . import utils
import feedparser


class IndexView(generic.ListView):
    """
    新着エピソードを表示する
    """
    model = Episode
    template_name = 'feed/index.html'
    # user = self.request.user
    paginate_by = 8
    queryset = Episode.objects.filter(
        # user=user,
        release_date__gt=datetime.date.today() - datetime.timedelta(days=20)
    ).order_by('-release_date')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # 登録用フォーム
        context['form'] = SubscriptionForm
        # TODO: フィルタリングがうまくできているかテストする
        context['likes'] = Like.objects.filter(
            created__gt=datetime.date.today() - datetime.timedelta(days=7),
        ).annotate(Count('user')).order_by('-user')[:8]
        return context


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

        # return render(
        #     request, 'feed/ch_detail.html', context={'channel': exist_ch[0]}
        # )
        return redirect('feed:ch_detail', pk=exist_ch[0].id)

    return render(request, 'feed/index.html')


class ChannelDetailView(generic.DetailView):
    """
    チャンネル詳細画面
    指定された登録チャンネルの最新エピソードを表示する
    """
    model = Channel
    template_name = 'feed/ch_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # 登録用フォーム
        context['form'] = SubscriptionForm
        context['episode'] = Episode.objects.filter(
            channel=context['channel']
        ).order_by('-release_date')
        return context


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
        # 登録用フォーム
        context['form'] = SubscriptionForm
        # TODO: フィルタリングがうまくできているかテストする
        context['like'] = Like.objects.filter(episode=context['episode'], user=user)
        return context


class EpisodeAllView(generic.TemplateView):
    """
    全チャンネルの未聴エピソードを表示
    """
    template_name = 'feed/ep_all.html'


class LikeListView(generic.ListView):
    """
    Likeされた全エピソードリストを表示
    """
    model = Like
    template_name = 'feed/like_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # 登録用フォーム
        context['form'] = SubscriptionForm
        return context


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


def change_like(request):
    """
    エピソードをLike登録する
    すでにLikeされている場合は削除する
    """
    if request.method == 'GET':
        query = request.GET.get('ep_id')
        # 登録エピソード取得
        episode = Episode.objects.filter(id=query)
        # 登録ユーザー取得
        user = request.user
        # 登録Likeデータ取得
        like = Like.objects.filter(episode=episode[0], user=user)

        if len(like) == 0:
            # Like登録
            utils.save_like(episode[0], user)
            response = {
                'btn_display': 'Likeから除外する'
            }
            return JsonResponse(response)
        else:
            # Likeから削除
            utils.delete_like(episode[0], user)
            response = {
                'btn_display': 'Like'
            }
            return JsonResponse(response)
