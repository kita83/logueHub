from django.urls import path
from . import views

app_name = 'feed'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('ch/<int:ch_cd>/', views.ChannelDetailView.as_view(), name='ch_detail'),
]