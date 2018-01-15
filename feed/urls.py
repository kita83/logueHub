from django.urls import path
from . import views

app_name = 'feed'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('all/', views.EpisodeAllView.as_view(), name='all'),
    path('like_list/', views.LikeListView.as_view(), name='like_list'),
    path('entry/', views.EntryView.as_view(), name='entry'),
    path('ch/detail/<int:pk>', views.ChannelDetailView.as_view(), name='ch_detail'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
]