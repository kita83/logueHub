from django.urls import reverse
from django.test import TestCase
from feed.models import Channel


class UrlResolveTest(TestCase):
    """URLディスパッチテスト"""
    def test_url_resoleves_to_index_view(self):
        """
        [get] /logue/ → feed/index.html
        """
        response = self.client.get('/logue/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed/index.html')

    def test_url_resoleves_to_ch_detail_view(self):
        """
        [post] /logue/ch/detail → feed/ch_detail.html
        """
        ch = Channel.objects.create(
            feed_url='https://example.com/test.rss'
        )
        response = self.client.post(
            reverse('feed:ch_detail', {'pk': ch.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed/ch_detail.html')


class FeedViewTest(TestCase):
    def test_index(self):
        """
        index画面にアクセスができる
        """
        pass

    def test_get_exist_url(self):
        """
        同一URLがあれば既存データを返す
        """
        ch = Channel.objects.create(
            feed_url='https://example.com/test.rss',
        )
        response = self.client.post(
            reverse('feed:entry', {'require_url': ch.feed_url})
        )
        self.assertEqual(response.status_code, 200)
        # 後で修正
        actual = response.title
        self.assertEqual(actual, 'test_title')

    def test_not_get_exist_url(self):
        """
        同一URLがなければ None を返す
        """
        Channel.objects.create(
            title='test_title',
            feed_url='http://feeds.test.fm/testfm',
            author_name='john'
        )
        ch = Channel.objects.filter(feed_url='http://feeds.test.fm/testfm')
        self.assertEqual(ch, None)

    # def test_did_not_save(self):
    #     """
    #     チャンネル情報に不備がある場合に登録されない.
    #     """
    #     feed_url = 'http://存在しない/testfm'
    #     ch = None
    #     utils.save_channel(ch, feed_url)
    #     actual = Channel.objects.filter(feed_url='http://feeds.test.fm/testfm')
    #     self.assertEqual(actual.count(), 0)
