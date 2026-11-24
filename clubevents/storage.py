"""Custom media storage helpers for ClubEvents."""

from cloudinary_storage.storage import MediaCloudinaryStorage
from django.conf import settings


class ClubEventsMediaStorage(MediaCloudinaryStorage):
    """Store uploaded posters and avatars on Cloudinary while keeping bundled
    demo SVG posters served from the local static/media route.
    """

    def url(self, name):
        """Return static/media route for repo-seeded demo posters, else Cloudinary URL."""
        if name and name.startswith("posters/demo/"):
            return f"{settings.MEDIA_URL}{name.lstrip('/')}"
        return super().url(name)
