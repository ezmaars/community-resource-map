"""URL routes for the resources app."""

from django.urls import path

from . import api, views

urlpatterns = [
    path("", views.home, name="home"),
    path("resources/", views.browse, name="browse"),
    path("resources/<slug:slug>/", views.resource_detail, name="resource_detail"),
    path("submit/", views.submit, name="submit"),
    path("submit/thank-you/", views.submit_success, name="submit_success"),
    path("manage/queue/", views.manage_queue, name="manage_queue"),
    # JSON API
    path("api/resources/", api.resources_geojson, name="api_resources"),
]
