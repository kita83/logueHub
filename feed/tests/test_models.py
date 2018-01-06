"""feedアプリのModelテスト"""
import feedparser
from django.test import TestCase
from feed.models import Channel
from feed import views


class ChannelModelTest(TestCase):
    """
    チャンネルモデル
    """
    def test_is_empty(self):
        saved_channels = Channel.objects.all()
        self.assertEqual(saved_channels.count(), 0)

    def test_save(self):
        """
        チャンネルの新規登録ができる
        """
        feed_url = 'http://feeds.rebuild.fm/rebuildfm'
        feeds = feedparser.parse(feed_url)
        ch = feeds.channel

        views.save_channel(ch, feed_url)
        c = Channel.objects.get(title='Rebuild')
        actual = c.link
        self.assertEqual(actual, 'http://rebuild.fm')

    def test_did_not_save(self):
        """
        チャンネル情報に不備がある場合に登録されない
        """
        feed_url = 'http://feeds.test.fm/testfm'
        ch = None
        views.save_channel(ch, feed_url)
        actual = Channel.objects.filter(feed_url='http://feeds.test.fm/testfm')
        self.assertEqual(actual.count(), 0)
