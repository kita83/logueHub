"""logue URL Configuration"""
from django.contrib import admin
from django.views.generic import RedirectView
from django.urls import include, path, re_path
from django.contrib.staticfiles import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from . import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logue/', include('feed.urls')),
    path('accounts/', include('allauth.urls')),
    path('', RedirectView.as_view(url='/logue', permanent=True)),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
        re_path(r'^static/(?P<path>.*)$', views.serve)
    ]

    urlpatterns += staticfiles_urlpatterns()
