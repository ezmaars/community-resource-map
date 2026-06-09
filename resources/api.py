"""
Minimal JSON API for the map.

We use a plain JsonResponse instead of Django REST Framework to keep the
dependency list short. The map fetches /api/resources/?<same query params>
and renders pins from the returned GeoJSON FeatureCollection.
"""

from django.http import JsonResponse

from .utils import filter_open_now
from .views import _apply_filters


def resources_geojson(request):
    qs, active = _apply_filters(request)
    resources = list(qs)

    if active["open_now"]:
        resources = filter_open_now(resources)

    features = []
    for r in resources:
        if not r.has_location:
            continue
        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    # GeoJSON order is [longitude, latitude].
                    "coordinates": [r.longitude, r.latitude],
                },
                "properties": {
                    "id": r.id,
                    "name": r.name,
                    "category": r.category.name,
                    "category_slug": r.category.slug,
                    "color": r.category.color or "#2f7d5b",
                    "icon": r.category.icon or "",
                    "is_free": r.is_free,
                    "address": r.full_address(),
                    "url": r.get_absolute_url(),
                },
            }
        )

    return JsonResponse(
        {"type": "FeatureCollection", "features": features},
        json_dumps_params={"ensure_ascii": False},
    )
