import pprint
import requests
from django.shortcuts import render


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
