"""feedアプリのモデル"""
from django.db import models
from django.conf import settings


class TimeStampModel(models.Model):
    """
    作成日時と変更日時フィールドを提供する Abstract クラス
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampModel):
    """
    カテゴリ情報を保持する
    """
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Channel(TimeStampModel):
    """
    チャンネル情報を保持する
    """
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    link = models.URLField(max_length=200, null=True, blank=True)
    feed_url = models.URLField(max_length=200)
    author_name = models.CharField(max_length=100)
    cover_image = models.ImageField(upload_to='images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Episode(TimeStampModel):
    """
    エピソード情報を保持する
    """
    channel = models.ForeignKey(Channel, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    link = models.URLField(max_length=200)
    description = models.TextField(null=True, blank=True)
    release_date = models.DateTimeField()
    duration = models.CharField(max_length=30, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Subscribe(TimeStampModel):
    """
    登録されたチャンネルを保持する
    """
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
    item_cd = models.CharField(max_length=50)
    type_cd = models.CharField(max_length=1)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
        )

    def __str__(self):
        return self.episode


class MstPlaylist(TimeStampModel):
    """
    プレイリスト情報を保持する
    """
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
    mstplaylist_cd = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
        )
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    play_order = models.IntegerField()

    def __str__(self):
        return self.episode


class Tag(TimeStampModel):
    """
    タグ付けされた情報を管理する
    """
    name = models.CharField(max_length=50)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
        )

    def __str__(self):
        return self.name
