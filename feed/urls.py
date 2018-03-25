from django.urls import path
from . import views

app_name = 'feed'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('channels/', views.ChannelAllView.as_view(), name='channels'),
    path('like_list/', views.LikeListView.as_view(), name='like_list'),
    path('entry/', views.entry, name='entry'),
    path('get_feed/', views.get_feed, name='get_feed'),
    path('likes/', views.LikeListView.as_view(), name='likes'),
    path('collection_list/', views.CollectionListView.as_view(), name='col_list'),
    path('collection/<uuid:mst_coll_id>/detail/', views.CollectionDetailView.as_view(), name='col_detail'),
    path('ch/<pk>/detail/', views.ChannelDetailView.as_view(), name='ch_detail'),
    path('ep/<pk>/detail/', views.EpisodeDetailView.as_view(), name='ep_detail'),
    path('change_like', views.change_like, name='change_like'),
    path('change_subscription', views.change_subscription, name='change_subscription'),
    path('add_collection', views.add_collection, name='add_collection'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('contact/', views.ContactView.as_view(), name='contact'),
]