"""Top-level URL configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

# Friendlier admin branding.
admin.site.site_header = "Community Resource Map — Administration"
admin.site.site_title = "Resource Map Admin"
admin.site.index_title = "Manage resources"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("resources.urls")),
]

# Serve user-uploaded media in development only.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error pages (templates live in templates/404.html and 500.html).
handler404 = "resources.views.handler404"
handler500 = "resources.views.handler500"
