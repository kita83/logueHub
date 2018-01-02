"""feedアプリのViewテスト"""
from django.test import TestCase, Client


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
