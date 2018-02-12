"""feedアプリのモデル"""
import uuid
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.db.models.signals import post_delete
from django.dispatch import receiver


class TimeStampModel(models.Model):
    """
    作成日時と変更日時フィールドを提供する Abstract クラス
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Channel(TimeStampModel):
    """
    チャンネル情報を保持する
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=2000, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    link = models.URLField(max_length=2000, null=True, blank=True)
    feed_url = models.URLField(max_length=200)
    author = models.CharField(max_length=100, null=True, blank=True)
    last_polled_time = models.DateTimeField(null=True, blank=True)
    cover_image = models.ImageField(
        upload_to='images/',
        width_field='width_field',
        height_field='height_field',
        null=True,
        blank=True
    )
    width_field = models.IntegerField(default=400)
    height_field = models.IntegerField(default=400)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title or self.feed_url

    def get_absolute_url(self):
        return reverse('feed:ch_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        """
        チャンネルを登録する
        """
        try:
            Channel.objects.get(feed_url=self.feed_url)
            super(Channel, self).save(*args, **kwargs)
        except Channel.DoesNotExist:
            super(Channel, self).save(*args, **kwargs)


@receiver(post_delete, sender=Channel)
def delete_file(sender, instance, **kwargs):
    """Channelモデル削除後に画像ファイルを削除する"""
    instance.cover_image.delete(False)


class Episode(TimeStampModel):
    """
    エピソード情報を保持する
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(Channel, on_delete=models.PROTECT)
    title = models.CharField(max_length=200, null=True, blank=True)
    link = models.URLField(max_length=2000, null=True, blank=True)
    audio_url = models.URLField(max_length=2000)
    description = models.TextField(null=True, blank=True)
    published_time = models.DateTimeField(null=True, blank=True)
    duration = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('feed:ep_detail', kwargs={'pk': self.pk})


class Subscription(TimeStampModel):
    """
    登録されたチャンネルを保持する
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(Channel, on_delete=models.PROTECT)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.user.email


class Like(TimeStampModel):
    """
    likeされたエピソードとユーザー情報を関連づける
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.episode.title


class MstCollection(TimeStampModel):
    """
    コレクション情報を保持する
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Collection(TimeStampModel):
    """
    コレクションに入れるチャンネルを管理する
    """
    mst_collection = models.ForeignKey(
        MstCollection,
        on_delete=models.CASCADE
    )
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.mst_collection.title


class MstPlaylist(TimeStampModel):
    """
    プレイリスト情報を保持する
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Playlist(TimeStampModel):
    """
    プレイリストに入れるエピソードを管理する
    """
    mst_playlist = models.ForeignKey(
        MstPlaylist,
        on_delete=models.CASCADE
    )
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    play_order = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.episode.title


class MstTag(TimeStampModel):
    """
    タグの名前を保持する
    """
    name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Tag(TimeStampModel):
    """
    タグ付けされた情報を管理する
    """
    mst_tag = models.ForeignKey(MstTag, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    def __str__(self):
        return self.mst_tag.name
