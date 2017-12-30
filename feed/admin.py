from django.contrib import admin
from .models import Channel, Episode, Category, Subscribe, Like, MstPlaylist, Playlist, Tag

admin.site.register(Channel)
admin.site.register(Episode)
admin.site.register(Category)
admin.site.register(Subscribe)
admin.site.register(Like)
admin.site.register(MstPlaylist)
admin.site.register(Playlist)
admin.site.register(Tag)
