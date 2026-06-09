"""
Data models for the Community Resource Map.

Design notes
------------
* Geolocation is stored as plain latitude/longitude floats rather than using
  GeoDjango/PostGIS. This keeps deployment light (no GDAL/PostGIS) and works
  identically on SQLite and PostgreSQL. Distance can be computed in Python with
  the haversine helper in utils.py. (Roadmap: swap in PostGIS for spatial queries.)
* Moderation and verification are first-class fields on Resource so the data
  model already supports the full review workflow described in the spec.
* Human-readable hours live in `hours_note`; optional structured rows in
  OperatingHours power the "Open now" filter when present.
"""

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _unique_slug(instance, value, slug_field="slug"):
    """Return a slug for `value` that is unique within the model's table."""
    base = slugify(value)[:240] or "item"
    candidate = base
    model = instance.__class__
    counter = 2
    qs = model.objects.all()
    if instance.pk:
        qs = qs.exclude(pk=instance.pk)
    while qs.filter(**{slug_field: candidate}).exists():
        candidate = f"{base}-{counter}"
        counter += 1
    return candidate


# -----------------------------------------------------------------------------
# Category & Tag
# -----------------------------------------------------------------------------
class Category(models.Model):
    """A top-level resource category, e.g. Food, Housing, Health."""

    name = models.CharField(_("name"), max_length=80, unique=True)
    slug = models.SlugField(_("slug"), max_length=90, unique=True, blank=True)
    description = models.CharField(_("description"), max_length=255, blank=True)
    # A short emoji or icon shortcode shown on category chips/cards.
    icon = models.CharField(
        _("icon"),
        max_length=8,
        blank=True,
        help_text=_("A single emoji used as the category icon, e.g. 🍎"),
    )
    color = models.CharField(
        _("color"),
        max_length=7,
        blank=True,
        help_text=_("Hex color for map pins/chips, e.g. #2f7d5b"),
    )
    order = models.PositiveIntegerField(_("display order"), default=0)

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """A reusable attribute such as 'Wheelchair accessible' or 'Walk-in'."""

    name = models.CharField(_("name"), max_length=60, unique=True)
    slug = models.SlugField(_("slug"), max_length=70, unique=True, blank=True)

    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.name)
        super().save(*args, **kwargs)


# -----------------------------------------------------------------------------
# Resource queryset / manager
# -----------------------------------------------------------------------------
class ResourceQuerySet(models.QuerySet):
    def approved(self):
        return self.filter(status=Resource.Status.APPROVED)

    def pending(self):
        return self.filter(status=Resource.Status.PENDING)

    def free_only(self):
        return self.filter(is_free=True)

    def search(self, query):
        if not query:
            return self
        return self.filter(
            models.Q(name__icontains=query)
            | models.Q(description__icontains=query)
            | models.Q(address__icontains=query)
            | models.Q(city__icontains=query)
            | models.Q(service_area__icontains=query)
        )


# -----------------------------------------------------------------------------
# Resource
# -----------------------------------------------------------------------------
class Resource(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending review")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")

    class Verification(models.TextChoices):
        UNVERIFIED = "unverified", _("Unverified")
        VERIFIED = "verified", _("Verified")
        OUTDATED = "outdated", _("Needs re-check")

    # --- Core info ---
    name = models.CharField(_("name"), max_length=160)
    slug = models.SlugField(_("slug"), max_length=180, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        verbose_name=_("category"),
        on_delete=models.PROTECT,
        related_name="resources",
    )
    description = models.TextField(_("description"))
    tags = models.ManyToManyField(Tag, verbose_name=_("tags"), blank=True, related_name="resources")

    # --- Location ---
    address = models.CharField(_("street address"), max_length=255, blank=True)
    city = models.CharField(_("city"), max_length=120, blank=True)
    state = models.CharField(_("state / region"), max_length=120, blank=True)
    postal_code = models.CharField(_("postal code"), max_length=20, blank=True)
    country = models.CharField(_("country"), max_length=120, blank=True, default="USA")
    latitude = models.FloatField(_("latitude"), null=True, blank=True)
    longitude = models.FloatField(_("longitude"), null=True, blank=True)
    service_area = models.CharField(
        _("service area"),
        max_length=255,
        blank=True,
        help_text=_("Who can use this, e.g. 'Open to all' or 'County residents'."),
    )

    # --- Contact ---
    phone = models.CharField(_("phone"), max_length=40, blank=True)
    email = models.EmailField(_("email"), blank=True)
    website = models.URLField(_("website"), blank=True)
    hours_note = models.CharField(
        _("hours (text)"),
        max_length=255,
        blank=True,
        help_text=_("Human-readable hours, e.g. 'Mon–Fri 9am–5pm'."),
    )

    # --- Cost ---
    is_free = models.BooleanField(_("free of charge"), default=True)
    cost_notes = models.CharField(
        _("cost notes"),
        max_length=255,
        blank=True,
        help_text=_("Only if not free, e.g. 'Sliding scale' or '$5 suggested'."),
    )

    # --- Moderation & verification ---
    status = models.CharField(
        _("status"), max_length=10, choices=Status.choices, default=Status.PENDING
    )
    verification = models.CharField(
        _("verification"),
        max_length=12,
        choices=Verification.choices,
        default=Verification.UNVERIFIED,
    )
    review_notes = models.TextField(_("internal review notes"), blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("submitted by"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_resources",
    )
    submitter_name = models.CharField(_("submitter name"), max_length=120, blank=True)
    submitter_email = models.EmailField(_("submitter email"), blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("reviewed by"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_resources",
    )
    reviewed_at = models.DateTimeField(_("reviewed at"), null=True, blank=True)

    # --- Timestamps ---
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    objects = ResourceQuerySet.as_manager()

    class Meta:
        verbose_name = _("resource")
        verbose_name_plural = _("resources")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["category", "status"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("resource_detail", args=[self.slug])

    @property
    def has_location(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def is_approved(self):
        return self.status == self.Status.APPROVED

    def is_open_now(self):
        """
        True/False if structured hours exist for the current weekday/time,
        or None when no structured hours are recorded (unknown).
        """
        if not self.opening_hours.exists():
            return None
        now = timezone.localtime()
        weekday = now.weekday()  # Monday=0 .. Sunday=6
        current = now.time()
        return self.opening_hours.filter(
            day_of_week=weekday,
            opens__lte=current,
            closes__gte=current,
        ).exists()

    def full_address(self):
        parts = [self.address, self.city, self.state, self.postal_code]
        return ", ".join(p for p in parts if p)


class OperatingHours(models.Model):
    """Optional structured opening hours that power the 'Open now' filter."""

    DAYS = [
        (0, _("Monday")),
        (1, _("Tuesday")),
        (2, _("Wednesday")),
        (3, _("Thursday")),
        (4, _("Friday")),
        (5, _("Saturday")),
        (6, _("Sunday")),
    ]

    resource = models.ForeignKey(
        Resource, on_delete=models.CASCADE, related_name="opening_hours"
    )
    day_of_week = models.PositiveSmallIntegerField(_("day"), choices=DAYS)
    opens = models.TimeField(_("opens"))
    closes = models.TimeField(_("closes"))

    class Meta:
        verbose_name = _("operating hours")
        verbose_name_plural = _("operating hours")
        ordering = ["day_of_week", "opens"]

    def __str__(self):
        return f"{self.get_day_of_week_display()} {self.opens}–{self.closes}"
