"""feedアプリのViewテスト"""
from django.test import TestCase, Client
from feed.models import Channel
from feed.views import get_exist_channel


class UrlResolveTest(TestCase):
    """URL解決テスト"""
    def test_url_resoleves_to_index_view(self):
        c = Client()
        response = c.get('/logue/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed/index.html')


class FeedViewTest(TestCase):
    def test_index(self):
        """
        index画面のアクセスができているかテストする
        """
        pass

    def test_get_exist_url(self):
        """
        同一URLがあれば既存データを返すことをチェック
        """
        Channel.objects.create(
            code=1,
            title='test_title',
            link='http://feeds.test.fm/testfm',
            author_name='john'
        )
        ch = get_exist_channel('http://feeds.test.fm/testfm')
        actual = ch[0].title
        self.assertEqual(actual, 'test_title')

    def test_not_get_exist_url(self):
        """
        同一URLがなければ None を返すことをチェック
        """
        Channel.objects.create(
            code=1,
            title='test_title',
            link='http://feeds.test.fm/testfm',
            author_name='john'
        )
        ch = get_exist_channel('http://feeds.notexisttest.fm/testfm')
        self.assertEqual(ch, None)
