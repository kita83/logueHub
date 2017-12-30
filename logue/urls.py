"""logue URL Configuration"""
from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.views.generic import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('logue/', include('feed.urls')),
    path('accounts/', include('allauth.urls')),
    path('', RedirectView.as_view(url='/logue', permanent=True)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
