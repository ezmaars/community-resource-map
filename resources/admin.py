"""Django admin — the full-power back office for staff."""

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Category, OperatingHours, Resource, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "order", "resource_count")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")

    @admin.display(description=_("resources"))
    def resource_count(self, obj):
        return obj.resources.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class OperatingHoursInline(admin.TabularInline):
    model = OperatingHours
    extra = 0


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "status",
        "verification",
        "is_free",
        "city",
        "created_at",
    )
    list_filter = ("status", "verification", "is_free", "category", "tags")
    search_fields = ("name", "description", "address", "city", "service_area")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ()
    filter_horizontal = ("tags",)
    readonly_fields = ("created_at", "updated_at", "reviewed_at", "reviewed_by")
    inlines = [OperatingHoursInline]
    list_per_page = 50
    actions = ["approve_selected", "reject_selected", "mark_verified"]

    fieldsets = (
        (None, {"fields": ("name", "slug", "category", "description", "tags")}),
        (
            _("Location"),
            {
                "fields": (
                    "address",
                    "city",
                    "state",
                    "postal_code",
                    "country",
                    ("latitude", "longitude"),
                    "service_area",
                )
            },
        ),
        (_("Contact"), {"fields": ("phone", "email", "website", "hours_note")}),
        (_("Cost"), {"fields": ("is_free", "cost_notes")}),
        (
            _("Moderation"),
            {
                "fields": (
                    "status",
                    "verification",
                    "review_notes",
                    "submitter_name",
                    "submitter_email",
                    "submitted_by",
                    "reviewed_by",
                    "reviewed_at",
                )
            },
        ),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )

    @admin.action(description=_("Approve selected resources"))
    def approve_selected(self, request, queryset):
        updated = queryset.update(
            status=Resource.Status.APPROVED,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, _("%(n)d resource(s) approved.") % {"n": updated})

    @admin.action(description=_("Reject selected resources"))
    def reject_selected(self, request, queryset):
        updated = queryset.update(
            status=Resource.Status.REJECTED,
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        self.message_user(request, _("%(n)d resource(s) rejected.") % {"n": updated})

    @admin.action(description=_("Mark selected as verified"))
    def mark_verified(self, request, queryset):
        updated = queryset.update(verification=Resource.Verification.VERIFIED)
        self.message_user(request, _("%(n)d resource(s) marked verified.") % {"n": updated})
