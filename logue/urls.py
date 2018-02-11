"""logue URL Configuration"""
from django.urls import include, path, re_path
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
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
        re_path(r'^static/(?P<path>.*)$', views.serve),
        # static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        # re_path(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        # static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    ]

    urlpatterns += staticfiles_urlpatterns()
