"""feedアプリのModelテスト"""
from django.test import TestCase
from .models import Channel

class ChannelModelTest(TestCase):
    """
    チャンネルモデル
    """
    def test_is_empty(self):
        saved_channels = Channel.objects.all()
        self.assertEqual(saved_channels.count(), 1)

    def test_bad_maths(self):
        self.assertEqual(1+1, 3)
