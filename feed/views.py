import logging

import markdown
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import generic
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required

from . import utils
from .forms import AddCollectionForm, ContactForm, SubscriptionForm
from .models import (Channel, Collection, Episode, Like, MstCollection,
                     Subscription)

logger = logging.getLogger(__name__)


class IndexView(generic.ListView):
    """トップページを表示する際のロジックを処理する."""
    model = Episode
    template_name = 'feed/index.html'
    context_object_name = 'episodes'
    paginate_by = 12

    def get_queryset(self):
        return Episode.recently.recently_published()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # 登録用フォーム
        context['subscription_form'] = SubscriptionForm
        # ログイン後であればコレクションタイトル取得
        user = self.request.user
        if hasattr(user, 'email'):
            context['mst_collection'] = MstCollection.objects.filter(user=user)
        # Like数の多いエピソードを取得
        id_list = Like.objects.values('episode').annotate(
            Count('episode')).order_by('-episode__count')[:10]
        con_list = []
        for item in id_list:
            con_list.append(Episode.objects.get(id=item['episode']))
        context['like_epsodes'] = con_list

        return context


@require_POST
class ChannelList(generic.DetailView):
    """チャンネル一覧ページを表示する際のロジックを処理する."""
    model = Channel
    template_name = 'feed/ch_detail.html'
    extra_context = {}

    def dispatch(self, request, *args, **kwargs):
        self.queryset = self.extra_context['channel_detail']
        return super(ChannelList, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ChannelList, self).get_context_data(**kwargs)
        # コレクションタイトル
        context['mst_collection'] = MstCollection.objects.filter(
            user=self.request.user)
        self.extra_context.update(context)
        return self.extra_context


@require_POST
@login_required
def entry(request):
    """入力された Feed URL をもとにチャンネル情報を登録する.

    Note:
        すでに登録がある場合は既存データを返す.

    Arguments:
        request (str) -- Feed URL.

    Returns:
        redirect -- チャンネル詳細ページへリダイレクト.
    """
    form = SubscriptionForm(request.POST)
    logger.info('Start Get Entry process...')

    if form.is_valid():
        # バリデート済の Feed URL を取得
        feed_url = form.cleaned_data['require_url']

        if not feed_url:
            logger.info('Required Feed URL does not match.')
            return render(request, 'feed/index.html')

        try:
            # すでに登録がある場合は既存データを表示する
            channel = Channel.objects.get(feed_url=feed_url)
            return redirect('feed:ch_detail', pk=channel.id)
        except Channel.DoesNotExist:
            logger.info('Save channel by required Feed URL %s.', feed_url)
            # Feed URL をもとに新規登録
            result = utils.get_feed(feed_url)
            # 登録成功の場合, チャンネル詳細ページへリダイレクトする
            if result == 'success':
                channel = Channel.objects.get(feed_url=feed_url)
                return redirect('feed:ch_detail', pk=channel.id)

    # バリデートエラーの場合、トップページに戻る
    logger.warning('WARNING: Invalid feed URL.')
    return redirect('feed:index')


@require_GET
@login_required
def change_subscription(request):
    """選択されたチャンネルの講読登録、あるいは講読解除をする.
    フロント側で Ajax 処理される.

    Arguments:
        channel_id (str) -- チャンネルID.

    Returns:
        JsonResponse -- 処理結果: bool.
    """
    query = request.GET.get('ch_id')

    # ユーザー情報、チャンネル情報を取得
    user = request.user
    channel = Channel.objects.get(id=query)
    sub = Subscription.objects.filter(channel=channel, user=user)

    # 登録の有無により、登録／解除を切り替える
    if not sub:
        Subscription.objects.get_or_create(channel=channel, user=user)
        response = {'subscription': True}
    else:
        Subscription.objects.filter(channel=channel, user=user).delete()
        response = {'subscription': False}

    return JsonResponse(response)


class ChannelDetailView(generic.DetailView):
    """チャンネルの最新エピソードを表示する.

    Arguments:
        channel_id (str) -- チャンネルID.

    Returns:
        context -- エピソードリスト.
        redirect -- チャンネル詳細ページへリダイレクト.
    """
    model = Channel
    template_name = 'feed/ch_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = self.request.user

        # ヘッダ部登録用フォーム
        context['subscription_form'] = SubscriptionForm
        # エピソードリスト
        context['episodes'] = Episode.objects.filter(
            channel=context['channel']).order_by('-published_time')[:8]

        # ログイン済の場合、登録状況に応じたデータを返す
        if hasattr(user, 'email'):
            # コレクション情報
            context['mst_collection'] = MstCollection.objects.filter(user=self.request.user)
            # 講読情報
            context['subscription'] = Subscription.objects.filter(
                channel=context['channel'], user=user)

        return context


class EpisodeDetailView(generic.DetailView):
    """エピソード詳細を表示する.

    Arguments:
        episode_id (str) -- チャンネルID.

    Returns:
        context -- エピソード詳細.
        redirect -- エピソード詳細ページへリダイレクト.
    """
    model = Episode
    template_name = 'feed/ep_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = self.request.user

        # ヘッダ部登録用フォーム
        context['subscription_form'] = SubscriptionForm
        # ShowNote の内容を Markdown 形式で渡す
        des = context['episode'].description
        context['parsed_description'] = markdown.markdown(des)

        # ログイン済の場合、登録状況に応じたデータを返す
        if hasattr(user, 'email'):
            # コレクション情報
            context['mst_collection'] = MstCollection.objects.filter(user=self.request.user)
            # コレクション追加フォーム
            col_form = AddCollectionForm()
            col_form.fields['add_collection'].queryset = MstCollection.objects.filter(user=user)
            context['add_collection'] = col_form
            # Like 情報
            context['like'] = Like.objects.filter(episode=context['episode'], user=user)
            # 講読情報
            context['subscription'] = Subscription.objects.filter(
                channel=context['episode'].channel, user=user)

        return context


class ChannelAllView(generic.ListView):
    """チャンネル一覧を表示する.

    Arguments:
        user_id (str) -- ユーザーID.

    Returns:
        context -- チャンネルリスト.
        redirect -- チャンネル一覧ページへリダイレクト.
    """
    model = Subscription
    template_name = 'feed/ch_all.html'
    context_object_name = 'subs'
    ordering = '-modified'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ChannelAllView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # ヘッダ部登録用フォーム
        context['subscription_form'] = SubscriptionForm
        # コレクション情報
        context['mst_collection'] = MstCollection.objects.filter(user=self.request.user)
        return context


class CollectionListView(generic.ListView):
    """コレクション一覧を表示する.

    Arguments:
        user_id (str) -- ユーザーID.

    Returns:
        context -- コレクションリスト.
        redirect -- コレクション一覧ページへリダイレクト.
    """
    model = MstCollection
    template_name = 'feed/col_list.html'
    context_object_name = 'mst_collection'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CollectionListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # 登録用フォーム
        context['subscription_form'] = SubscriptionForm
        return context


class CollectionDetailView(generic.ListView):
    """コレクション詳細を表示する.

    Arguments:
        mst_collection_id (str) -- コレクションID.

    Returns:
        context -- コレクション詳細.
        redirect -- コレクション詳細ページへリダイレクト.
    """
    model = Collection
    template_name = 'feed/col_detail.html'
    context_object_name = 'collection'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CollectionDetailView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(mst_collection_id=self.kwargs['mst_coll_id'])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # ヘッダ部登録用フォーム
        context['subscription_form'] = SubscriptionForm
        # コレクション情報
        context['mst_collection'] = MstCollection.objects.filter(user=self.request.user)
        # コレクションタイトル
        context['title'] = context['collection'][0].mst_collection.title
        return context


class LikeListView(generic.ListView):
    """Likeされた全エピソードリストを表示する.

    Arguments:
        mst_collection_id (str) -- コレクションID.

    Returns:
        context -- コレクション詳細.
        redirect -- Like 済のエピソード一覧ページへリダイレクト.
    """
    model = Like
    template_name = 'feed/like_list.html'
    context_object_name = 'likes'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LikeListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return Like.objects.filter(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # コレクション情報
        context['mst_collection'] = MstCollection.objects.filter(user=self.request.user)
        # ヘッダ部登録用フォーム
        context['subscription_form'] = SubscriptionForm
        return context


class SettingsView(generic.TemplateView):
    """各種設定項目を表示する.

    Todo:
        未実装.
    """
    template_name = 'feed/settings.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # コレクションタイトル
        context['mst_collection'] = MstCollection.objects.filter(user=self.request.user)
        # 登録用フォーム
        context['subscription_form'] = SubscriptionForm
        return context


class TermsView(generic.TemplateView):
    """利用規約を表示する.

    Returns:
        redirect -- 利用規約ページへリダイレクト.
    """
    template_name = 'feed/terms.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = self.request.user

        # ヘッダ部登録用フォーム
        context['subscription_form'] = SubscriptionForm

        # ログイン後であればコレクションタイトル取得
        if hasattr(user, 'email'):
            context['mst_collection'] = MstCollection.objects.filter(user=user)

        return context


class PrivacyView(generic.TemplateView):
    """プラバシーポリシーを表示する.

    Returns:
        redirect -- プラバシーポリシーページへリダイレクト.
    """
    template_name = 'feed/privacy.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = self.request.user

        # ヘッダ部登録用フォーム
        context['subscription_form'] = SubscriptionForm

        # ログイン後であればコレクションタイトル取得
        if hasattr(user, 'email'):
            context['mst_collection'] = MstCollection.objects.filter(user=user)

        return context


@require_GET
@login_required
def change_like(request):
    """選択されたチャンネルの Like 登録、あるいは Like 解除をする.
    フロント側で Ajax 処理される.

    Arguments:
        episode_id (str) -- エピソードID.

    Returns:
        JsonResponse -- 処理結果: bool.
    """
    query = request.GET.get('ep_id')

    # ユーザー情報、エピソード情報を取得
    episode = Episode.objects.get(id=query)
    user = request.user
    # 登録 Like データ取得
    like = Like.objects.filter(episode=episode, user=user)

    # 登録の有無により、登録／解除を切り替える
    if not like:
        Like.objects.create(episode=episode, user=user)
        response = {'liked': True}
    else:
        Like.objects.filter(episode=episode, user=user).delete()
        response = {'liked': False}

    return JsonResponse(response)


@require_GET
@login_required
def add_collection(request):
    """エピソードをコレクションに追加する.
    フロント側で Ajax 処理される.

    Arguments:
        episode_id (str) -- エピソードID.

    Returns:
        JsonResponse -- 処理結果.
    """

    # 新規登録用タイトルを取得
    new_title = request.GET.get('new_title')
    # 登録対象のエピソードID、コレクションIDを取得
    ep_id = request.GET.get('ep_id')
    mst_id = request.GET.get('col_id')

    # 新規登録用タイトル、または既存コレクションIDが取得できない場合
    if new_title and mst_id:
        return JsonResponse({'result': 'no_args'})

    # ユーザー情報、エピソード情報を取得
    user = request.user
    episode = Episode.objects.get(id=ep_id)

    # 新規登録用タイトルの有無により、新規登録／既存コレクションに追加 を振り分ける
    if not new_title:
        mst = MstCollection.objects.get(id=mst_id)
    else:
        mst = MstCollection.objects.create(title=new_title, user=user)

    # エピソード登録
    col, created = Collection.objects.get_or_create(mst_collection=mst, episode=episode)

    return JsonResponse({'result': 'success'}) if created else JsonResponse({'result': 'registerd'})


@require_GET
@login_required
def remove_collection(request):
    """コレクションに登録されたエピソードを削除する.

    Arguments:
        episode_id (str) -- エピソードID.
        collection_id (str) -- コレクションID.

    Returns:
        JsonResponse -- 処理結果: bool.
    """
    # 登録マスタコレクション、エピソード取得
    mst_id = request.GET.get('mst_id')
    ep_id = request.GET.get('ep_id')
    mst = MstCollection.objects.get(id=mst_id)
    episode = Episode.objects.get(id=ep_id)

    # コレクションに登録があれば削除する
    if mst:
        Collection.objects.filter(mst_collection=mst, episode=episode).delete()
        response = {'isSuccess': True}
    else:
        response = {'isSuccess': False}

    return JsonResponse(response)


class ContactView(generic.FormView):
    """コンタクトページを表示する.

    Returns:
        redirect -- コンタクトページへリダイレクト.
    """
    template_name = 'feed/contact.html'
    form_class = ContactForm
    success_url = '/'

    def form_valid(self, form):
        form.send_email()
        return super(ContactView, self).form_valid(form)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        user = self.request.user
        # ヘッダ部登録用フォーム
        context['subscription_form'] = SubscriptionForm
        # ログイン後であればコレクションタイトル取得
        if hasattr(user, 'email'):
            context['mst_collection'] = MstCollection.objects.filter(user=self.request.user)
        return context
