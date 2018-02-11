from django.utils import timezone
from django.test import TestCase
from feed.models import Channel, Episode, Subscription, Like
from accounts.models import LogueUser


class ChannelModelTest(TestCase):
    """
    チャンネルモデル
    """
    def test_save(self):
        """
        チャンネルの新規登録ができる.
        """
        Channel.objects.create(
            title='examplefm',
            description='testtesttest',
            link='https://example.com',
            feed_url='https://example.com/test.rss',
            author='tester',
            last_polled_time=timezone.now(),
            cover_image='images/123456789.png',
            width_field=200,
            height_field=200
        )
        ch = Channel.objects.get(title='examplefm')
        actual = ch.link
        self.assertEqual(actual, 'https://example.com')


class EpisodeModelTest(TestCase):
    """
    エピソードモデル
    """
    def test_save(self):
        """
        エピソードの新規登録ができる
        """
        ch = Channel.objects.create(
            title='examplefm',
            description='testtesttest',
            link='https://example.com',
            feed_url='https://example.com/test.rss',
            author='tester',
            last_polled_time=timezone.now(),
            cover_image='images/123456789.png',
            width_field=200,
            height_field=200
        )
        Episode.objects.create(
            channel=ch,
            title='test_title',
            link='http://example.fm',
            audio_url='http://files.example.fm/exampple-ep27.mp3',
            description='description',
            published_time=timezone.now(),
            duration='35:12',
        )
        ep = Episode.objects.get(title='test_title')
        actual = ep.link
        self.assertEqual(actual, 'http://example.fm')


class SubscriptionModelTest(TestCase):
    """
    購読モデル
    """
    def test_save(self):
        """
        購読情報の新規登録ができる
        """
        user = LogueUser.objects.create_user(
            email='test@example.com', password='testtesttest')
        ch = Channel.objects.create(
            title='examplefm',
            description='testtesttest',
            link='https://example.com',
            feed_url='https://example.com/test.rss',
            author='tester',
            last_polled_time=timezone.now(),
            cover_image='images/123456789.png',
            width_field=200,
            height_field=200
        )
        Subscription.objects.create(
            channel=ch,
            user=user
        )
        sub = Subscription.objects.get(channel=ch, user=user)
        actual = sub.user.email
        self.assertEqual(actual, 'test@example.com')
        actual = sub.channel.title
        self.assertEqual(actual, 'examplefm')


class LikeModelTest(TestCase):
    """
    Likeモデル
    """
    def test_save(self):
        """
        Likeの新規登録ができる
        """
        user = LogueUser.objects.create_user(
            email='test@example.com', password='testtesttest')
        ch = Channel.objects.create(
            title='examplefm',
            description='testtesttest',
            link='https://example.com',
            feed_url='https://example.com/test.rss',
            author='tester',
            last_polled_time=timezone.now(),
            cover_image='images/123456789.png',
            width_field=200,
            height_field=200
        )
        ep = Episode.objects.create(
            channel=ch,
            title='test_title',
            link='http://example.fm',
            audio_url='http://files.example.fm/exampple-ep27.mp3',
            description='description',
            published_time=timezone.now(),
            duration='35:12',
        )
        Like.objects.create(
            episode=ep,
            user=user
        )
        like = Like.objects.get(episode=ep, user=user)
        actual = like.user.email
        self.assertEqual(actual, 'test@example.com')
        actual = like.episode.title
        self.assertEqual(actual, 'test_title')
