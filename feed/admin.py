from django.contrib import admin
from feed import models

admin.site.register(models.Channel)
admin.site.register(models.Episode)
admin.site.register(models.Subscription)
admin.site.register(models.Like)
admin.site.register(models.MstCollection)
admin.site.register(models.Collection)
admin.site.register(models.MstPlaylist)
admin.site.register(models.Playlist)
admin.site.register(models.MstTag)
admin.site.register(models.Tag)
