import pprint
import requests
import feedparser
from django.shortcuts import render
from django.views import View
from .forms import SubscribeForm
from .models import Channel, Episode


class IndexView(View):
    template_name = 'feed/index.html'

    def post(self, request, *args, **kwargs):
        """フィード登録項目に入力がある場合、チャンネル登録処理をする"""
        form = SubscribeForm(request.POST)

        if form.is_valid():
            url = form.cleaned_data['require_url']

            # 入力されたURLがすでに登録されている場合、DBからデータを取得
            exist_ch = get_exist_channel(url)

            forms = []
            if exist_ch:
                # チャンネルから最新エピソードを取得
                exist_ep = get_exist_epsode(exist_ch[0])

                for ep in exist_ep:
                    form = {
                        'title': ep.title,
                        'link': ep.link,
                        'description': ep.description,
                        'released_at': ep.released_at
                    }
                    forms.append(form)
            else:
                # 入力されたURLからFeed情報を取得
                feeds = parse_feed(url)

                for ep in feeds:
                    form = {
                        'title': ep.title,
                        'link': ep.link,
                        'description': ep.description,
                        'released_at': ep.released_at
                    }
                    forms.append(form)
            return render(request, 'feed/ch_detail.html', {'forms': forms})

        return render(request, self.template_name, {'form': form})

    def get(self, request):
        form = SubscribeForm()
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

        return render(request, self.template_name, {
            'feeds': feeds,
            'form': form
        })


class ChannelDetailView(View):
    template_name = 'feed/ch_detail.html'

    def get(self, request):
        """
        チャンネル詳細画面

        指定された登録チャンネルの最新エピソードを表示する
        """
        new = []
        tmp = {
            'title': 'ep0001',
            'author': 'chris',
            'released_at': '2017年12月30日'
        }
        new.append(tmp)
        context = {
            'new_list': new
        }
        return render(request, self.template_name, context=context)


def get_exist_channel(require_url):
    """
    登録済みのチャンネルデータを返す
    存在しない場合: None
    """
    rtn = Channel.objects.filter(link=require_url)
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


def parse_feed(url):
    """
    URLからfeedデータを取得する
    """
    feed = feedparser.parse(url)
    save_channel(feed)
    feeds = {}
    return feeds


def save_channel(feed):
    """
    feedデータをChannelに登録する
    """
    pass