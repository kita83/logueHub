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


class Channel(TimeStampModel):
    """
    チャンネル情報を保持する
    """
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    link = models.URLField(max_length=200, null=True, blank=True)
    feed_url = models.URLField(max_length=200)
    author_name = models.CharField(max_length=100, null=True, blank=True)
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


class Subscription(TimeStampModel):
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


class MstCollection(TimeStampModel):
    """
    コレクション情報を保持する
    """
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
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.mst_collection.title


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
