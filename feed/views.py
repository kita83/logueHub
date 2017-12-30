import pprint
import requests
from django.shortcuts import render
from django.views import View


class IndexView(View):
    template_name = 'feed/index.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            return render(request, 'feed/ch_detail.html', {'form': form})

        return render(request, self.template_name, {'form': form})

    def get(self, request):
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

        return render(request, self.template_name, context=context)


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
