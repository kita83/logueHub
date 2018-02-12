import datetime
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.views import generic
from django.http import JsonResponse
from django.db.models import Count
from .forms import SubscriptionForm
from .models import Channel, Episode, Like, Subscription
from . import utils

import logging

logger = logging.getLogger(__name__)


class IndexView(generic.ListView):
    """
    新着エピソードを表示する
    """
    model = Episode
    template_name = 'feed/index.html'
    context_object_name = 'episodes'
    paginate_by = 8
    queryset = Episode.objects.filter(
        # user=user,
        published_time__gt=datetime.date.today() - datetime.timedelta(days=20)
    ).order_by('-published_time')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # 登録用フォーム
        context['subscription_form'] = SubscriptionForm
        # TODO: フィルタリングがうまくできているかテストする
        context['likes'] = Like.objects.filter(
                created__gt=datetime.date.today() - datetime.timedelta(days=7),
            ).annotate(Count('user')).order_by('-user')[:8]
        return context


@require_POST
class ChannelList(generic.DetailView):
    """List of Channel"""
    model = Channel
    template_name = 'feed/ch_detail.html'
    extra_context = {}

    def dispatch(self, request, *args, **kwargs):
        self.extra_context = utils.build_context(request)
        self.queryset = self.extra_context['channel_detail']
        return super(ChannelList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ChannelList, self).get_context_data(**kwargs)
        self.extra_context.update(context)
        return self.extra_context


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

        if not feed_url:
            return render(request, 'feed/index.html')

        # チャンネル新規登録または、既存データ取得
        channel, created = Channel.objects.get_or_create(feed_url=feed_url)

        # チャンネルが新規登録された場合, チャンネル、エピソードの最新情報を更新
        if created:
            utils.poll_feed(channel)

        # 購読情報を登録
        Subscription.objects.get_or_create(
            channel=channel,
            user=user
        )
        return redirect('feed:ch_detail', pk=channel.id)

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
        context['subscription_form'] = SubscriptionForm
        context['episodes'] = Episode.objects.filter(
            channel=context['channel']
        ).order_by('-published_time')[:8]
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
        context['subscription_form'] = SubscriptionForm
        # TODO: フィルタリングがうまくできているかテストする
        context['like'] = Like.objects.filter(
            episode=context['episode'], user=user)
        context['channel'] = Channel.objects.get(
            id=context['episode'].channel.id)
        return context


class ChannelAllView(generic.ListView):
    """
    全チャンネルの未聴エピソードを表示
    """
    model = Channel
    template_name = 'feed/ch_all.html'
    context_object_name = 'channels'
    ordering = '-modified'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # 登録用フォーム
        context['subscription_form'] = SubscriptionForm
        return context


class LikeListView(generic.ListView):
    """
    Likeされた全エピソードリストを表示
    """
    model = Like
    template_name = 'feed/like_list.html'
    context_object_name = 'likes'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # 登録用フォーム
        context['subscription_form'] = SubscriptionForm
        return context


class SettingsView(generic.TemplateView):
    """
    各種設定項目を表示
    """
    template_name = 'feed/settings.html'


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
            Like.objects.create(
                episode=episode[0],
                user=user
            )
            response = {
                'btn_display': 'Likeから除外する'
            }
            return JsonResponse(response)
        else:
            # Likeから削除
            Like.objects.filter(
                episode=episode[0],
                user=user
            ).delete()
            response = {
                'btn_display': 'Like'
            }
            return JsonResponse(response)
