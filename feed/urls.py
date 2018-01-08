from django.urls import path
from . import views

app_name = 'feed'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('ch/create/', views.ChannelCreateView.as_view(), name='ch_create'),
    path('ch/detail/', views.ChannelDetailView.as_view(), name='ch_detail'),
]