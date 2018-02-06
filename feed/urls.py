from django.urls import path
from . import views

app_name = 'feed'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('all/', views.EpisodeAllView.as_view(), name='all'),
    path('like_list/', views.LikeListView.as_view(), name='like_list'),
    path('entry/', views.entry, name='entry'),
    path('likes/', views.LikeListView.as_view(), name='likes'),
    path('ch/<pk>/detail/', views.ChannelDetailView.as_view(), name='ch_detail'),
    path('ep/<pk>/detail/', views.EpisodeDetailView.as_view(), name='ep_detail'),
    # path('collection/', views.CollectionDetailView.as_view(), name='collection_detail'),
    path('change_like', views.change_like, name='change_like'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
]