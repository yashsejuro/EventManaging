"""Top-level URL routing for ClubEvents."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView
from django.views.static import serve


urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url="/static/images/favicon.svg", permanent=True)),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("events.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

# Django's development helper serves uploaded posters; a real deployment uses
# a web server or object storage for media instead.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
