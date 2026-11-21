"""Top-level URL routing for ClubEvents."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("events.urls")),
]

# Django's development helper serves uploaded posters; a real deployment uses
# a web server or object storage for media instead.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
