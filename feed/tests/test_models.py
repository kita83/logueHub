"""feedアプリのModelテスト"""
from django.test import TestCase
from feed.models import Channel

class ChannelModelTest(TestCase):
    """
    チャンネルモデル
    """
    def test_is_empty(self):
        saved_channels = Channel.objects.all()
        self.assertEqual(saved_channels.count(), 0)
