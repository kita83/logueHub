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
    cd = models.IntegerField(primary_key=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=100)
    author_name = models.CharField(max_length=100)
    cover_image = models.ImageField(upload_to='images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Episode(TimeStampModel):
    """
    エピソード情報を保持する
    """
    cd = models.IntegerField(primary_key=True)
    channel = models.ForeignKey(Channel, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    link = models.URLField(max_length=200)
    summary = models.TextField(null=True, blank=True)
    release_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Like(TimeStampModel):
    """
    Likeされたエピソードとユーザー情報を関連づける
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    def __str__(self):
        return self.episode

class Stock(TimeStampModel):
    """
    Stockされたエピソードとユーザー情報を関連づける
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    def __str__(self):
        return self.episode


class Follow(TimeStampModel):
    """
    Followされたエピソードとユーザー情報を関連づける
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    def __str__(self):
        return self.episode


class MstTag(TimeStampModel):
    """
    タグのマスタ情報を保持する
    """
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Tag(TimeStampModel):
    """
    タグ付けされたエピソードとユーザー情報を関連づける
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mst_tag = models.ForeignKey(MstTag, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE)

    def __str__(self):
        return self.mst_tag
