import pprint
import requests
from django.shortcuts import render, redirect
from allauth import account


def index(request):
    """
    トレンド一覧画面

    iTunes APIからPodcastランキングを取得する
    :param request:
    :return: context:
    """

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
        released_at = feed['im:releaseDate']['attributes']['label']
        tmp = {
            'title': title,
            'channel': channel,
            'author': author,
            'released_at': released_at
        }
        feeds.append(tmp)

    # debug
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(feeds)

    context = {
        'feeds': feeds
    }

    return render(request, 'index.html', context)


class LoginView(account.views.LoginView):
    """
    ログインページへ遷移
    """
    template_name = 'login.html'
    ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False

    def dispatch(self, request, *args, **kwargs):
        response = super(LoginView, self).dispatch(request, *args, **kwargs)
        return response

    def form_valid(self, form):
        return super(LoginView, self).form_valid(form)


login = LoginView.as_view()


class LogoutView(account.views.LogoutView):
    """
    ログアウトページへ遷移
    """
    template_name = 'logout.html'
    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def post(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            self.logout()
        return redirect('/')


logout = LogoutView.as_view()


class SignupView(account.views.SignupView):
    """
    サインアップページへ遷移
    """
    template_name = 'signup.html'
    ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False

    def get_context_data(self, **kwargs):
        context = super(SignupView, self).get_context_data(**kwargs)
        return context


signup = SignupView.as_view()
