"""Template context processors."""

from django.conf import settings


def site_settings(request):
    """Expose a few global values to every template."""
    return {
        "MAP_DEFAULT_LAT": settings.MAP_DEFAULT_LAT,
        "MAP_DEFAULT_LNG": settings.MAP_DEFAULT_LNG,
        "MAP_DEFAULT_ZOOM": settings.MAP_DEFAULT_ZOOM,
        "SITE_NAME": "Community Resource Map",
    }
