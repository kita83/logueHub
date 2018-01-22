"""feedアプリのViewテスト"""
from django.test import TestCase
from feed.models import Channel
from feed.utils import get_exist_channel


class UrlResolveTest(TestCase):
    """URL解決テスト"""
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
        response = self.client.post(
            '/logue/ch/detail/',
            {'require_url': 'http://feeds.rebuild.fm/rebuildfm'}
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
        Channel.objects.create(
            title='test_title',
            feed_url='http://feeds.test.fm/testfm',
            author_name='john'
        )
        ch = get_exist_channel('http://feeds.test.fm/testfm')
        actual = ch[0].title
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
        ch = get_exist_channel('http://feeds.notexisttest.fm/testfm')
        self.assertEqual(ch, None)
