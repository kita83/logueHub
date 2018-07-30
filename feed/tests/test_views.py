from unittest import mock

from django.urls import reverse
from django.test import TestCase

from feed.models import Channel
from accounts.models import LogueUser


class UrlResolveTest(TestCase):
    """URLディスパッチテスト."""
    def test_url_resoleves_to_index_view(self):
        """/logue/ にアクセス時に feed/index.html が呼ばれることを検証.

        Method:
            GET
        """
        response = self.client.get('/logue/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed/index.html')

    def test_url_resoleves_to_ch_detail_view(self):
        """/logue/ch/detail にアクセス時に feed/ch_detail.html が呼ばれることを検証.

        Method:
            POST
        """
        ch = Channel.objects.create(
            feed_url='https://example.com/test.rss'
        )
        response = self.client.get(
            reverse('feed:ch_detail', kwargs={'pk': ch.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed/ch_detail.html')

    def test_redirect_login(self):
        """未ログインの場合、ログインページへリダイレクトされる."""
        response = self.client.post(
            '/logue/channels/', {'user': 'AnonymousUser', 'password': ''})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, '/accounts/login/?next=/logue/channels/')

        response = self.client.post(
            '/logue/like_list/', {'user': 'AnonymousUser', 'password': ''})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, '/accounts/login/?next=/logue/like_list/')

        response = self.client.post(
            '/logue/entry/', {'user': 'AnonymousUser', 'password': ''})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/logue/entry/')

        response = self.client.post(
            '/logue/likes/', {'user': 'AnonymousUser', 'password': ''})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/logue/likes/')

        response = self.client.post(
            '/logue/collection_list/', {
                'user': 'AnonymousUser', 'password': ''})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, '/accounts/login/?next=/logue/collection_list/')


class FeedViewTest(TestCase):
    """Feed登録時に関するテスト."""
    def setUp(self):
        self.user = LogueUser.objects.create(email='example.com')
        self.exist_ch = Channel.objects.create(
            feed_url='https://example.com/test.rss',
        )

    def test_get_exist_url(self):
        """登録済の Feed URL 登録リクエストがあれば、既存のデータを返す."""
        actual = self.exist_ch.id
        self.client.post(
            reverse('feed:entry'), {
                'user': self.user,
                'require_url': self.exist_ch.feed_url
            }
        )
        get_ch = Channel.objects.filter(feed_url='https://example.com/test.rss')
        # 取得したIDが同じであることを確認
        self.assertEqual(actual, get_ch[0].id)

    def test_did_not_exist_feed_url(self):
        """リクエスト Feed URL が存在しない場合に登録されない."""
        feed_url = 'http://存在しない/testfm'
        self.client.post(
            reverse('feed:entry'), {
                'user': self.user,
                'feed_url': feed_url
            }
        )
        actual = Channel.objects.filter(feed_url=feed_url)
        # 登録件数が0件であることを確認
        self.assertEqual(actual.count(), 0)

    def test_can_not_get_audio_url(self):
        """オーティオURLが存在しない場合に登録されない."""
        m = mock.MagicMock()
        m.get_feed('request_feed')
        m.get_feed.return_value = {
            'feed': {
                'title': 'test',
                'title_detail': {
                    'type': 'text/plain',
                    'value': 'test title detail'
                },
                'entries': [
                    {'links': []}
                ]
            }
        }

        feed_url = 'http://存在しない/testfm'
        self.client.post(
            reverse('feed:entry'), {
                'user': self.user,
                'feed_url': feed_url

            }
        )
        actual = Channel.objects.filter(feed_url=feed_url)
        # 登録件数が0件であることを確認
        self.assertEqual(actual.count(), 0)