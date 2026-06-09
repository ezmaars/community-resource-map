"""Small reusable helpers (no third-party dependencies)."""

from math import asin, cos, radians, sin, sqrt


def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance between two points in kilometers."""
    r = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lng = radians(lng2 - lng1)
    a = (
        sin(d_lat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lng / 2) ** 2
    )
    return 2 * r * asin(sqrt(a))


def filter_open_now(resources):
    """
    Return only resources currently open, given an iterable of Resource objects.

    Resources without structured hours (is_open_now() is None) are treated as
    "unknown" and excluded from the strict 'Open now' filter. We evaluate in
    Python to stay database-agnostic; see the roadmap for moving this into SQL.
    """
    return [r for r in resources if r.is_open_now() is True]
