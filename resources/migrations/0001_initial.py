import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ------------------------------------------------------------------ #
        # Category                                                            #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=80, unique=True, verbose_name="name")),
                ("slug", models.SlugField(blank=True, max_length=90, unique=True, verbose_name="slug")),
                ("description", models.CharField(blank=True, max_length=255, verbose_name="description")),
                (
                    "icon",
                    models.CharField(
                        blank=True,
                        help_text="A single emoji used as the category icon, e.g. 🍎",
                        max_length=8,
                        verbose_name="icon",
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        blank=True,
                        help_text="Hex color for map pins/chips, e.g. #2f7d5b",
                        max_length=7,
                        verbose_name="color",
                    ),
                ),
                ("order", models.PositiveIntegerField(default=0, verbose_name="display order")),
            ],
            options={
                "verbose_name": "category",
                "verbose_name_plural": "categories",
                "ordering": ["order", "name"],
            },
        ),
        # ------------------------------------------------------------------ #
        # Tag                                                                 #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=60, unique=True, verbose_name="name")),
                ("slug", models.SlugField(blank=True, max_length=70, unique=True, verbose_name="slug")),
            ],
            options={
                "verbose_name": "tag",
                "verbose_name_plural": "tags",
                "ordering": ["name"],
            },
        ),
        # ------------------------------------------------------------------ #
        # Resource                                                            #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="Resource",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=160, verbose_name="name")),
                ("slug", models.SlugField(blank=True, max_length=180, unique=True, verbose_name="slug")),
                ("description", models.TextField(verbose_name="description")),
                # --- Location ---
                ("address", models.CharField(blank=True, max_length=255, verbose_name="street address")),
                ("city", models.CharField(blank=True, max_length=120, verbose_name="city")),
                ("state", models.CharField(blank=True, max_length=120, verbose_name="state / region")),
                ("postal_code", models.CharField(blank=True, max_length=20, verbose_name="postal code")),
                ("country", models.CharField(blank=True, default="USA", max_length=120, verbose_name="country")),
                ("latitude", models.FloatField(blank=True, null=True, verbose_name="latitude")),
                ("longitude", models.FloatField(blank=True, null=True, verbose_name="longitude")),
                (
                    "service_area",
                    models.CharField(
                        blank=True,
                        help_text="Who can use this, e.g. 'Open to all' or 'County residents'.",
                        max_length=255,
                        verbose_name="service area",
                    ),
                ),
                # --- Contact ---
                ("phone", models.CharField(blank=True, max_length=40, verbose_name="phone")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email")),
                ("website", models.URLField(blank=True, verbose_name="website")),
                (
                    "hours_note",
                    models.CharField(
                        blank=True,
                        help_text="Human-readable hours, e.g. 'Mon–Fri 9am–5pm'.",
                        max_length=255,
                        verbose_name="hours (text)",
                    ),
                ),
                # --- Cost ---
                ("is_free", models.BooleanField(default=True, verbose_name="free of charge")),
                (
                    "cost_notes",
                    models.CharField(
                        blank=True,
                        help_text="Only if not free, e.g. 'Sliding scale' or '$5 suggested'.",
                        max_length=255,
                        verbose_name="cost notes",
                    ),
                ),
                # --- Moderation & verification ---
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending review"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                        ],
                        default="pending",
                        max_length=10,
                        verbose_name="status",
                    ),
                ),
                (
                    "verification",
                    models.CharField(
                        choices=[
                            ("unverified", "Unverified"),
                            ("verified", "Verified"),
                            ("outdated", "Needs re-check"),
                        ],
                        default="unverified",
                        max_length=12,
                        verbose_name="verification",
                    ),
                ),
                ("review_notes", models.TextField(blank=True, verbose_name="internal review notes")),
                ("submitter_name", models.CharField(blank=True, max_length=120, verbose_name="submitter name")),
                ("submitter_email", models.EmailField(blank=True, max_length=254, verbose_name="submitter email")),
                ("reviewed_at", models.DateTimeField(blank=True, null=True, verbose_name="reviewed at")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
                # --- FK: category ---
                (
                    "category",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="resources",
                        to="resources.category",
                        verbose_name="category",
                    ),
                ),
                # --- FK: submitted_by ---
                (
                    "submitted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="submitted_resources",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="submitted by",
                    ),
                ),
                # --- FK: reviewed_by ---
                (
                    "reviewed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reviewed_resources",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="reviewed by",
                    ),
                ),
                # --- M2M: tags ---
                (
                    "tags",
                    models.ManyToManyField(
                        blank=True,
                        related_name="resources",
                        to="resources.tag",
                        verbose_name="tags",
                    ),
                ),
            ],
            options={
                "verbose_name": "resource",
                "verbose_name_plural": "resources",
                "ordering": ["name"],
                "indexes": [
                    models.Index(fields=["status"], name="resources_r_status_idx"),
                    models.Index(fields=["category", "status"], name="resources_r_cat_status_idx"),
                ],
            },
        ),
        # ------------------------------------------------------------------ #
        # OperatingHours                                                      #
        # ------------------------------------------------------------------ #
        migrations.CreateModel(
            name="OperatingHours",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "day_of_week",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Monday"),
                            (1, "Tuesday"),
                            (2, "Wednesday"),
                            (3, "Thursday"),
                            (4, "Friday"),
                            (5, "Saturday"),
                            (6, "Sunday"),
                        ],
                        verbose_name="day",
                    ),
                ),
                ("opens", models.TimeField(verbose_name="opens")),
                ("closes", models.TimeField(verbose_name="closes")),
                (
                    "resource",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="opening_hours",
                        to="resources.resource",
                    ),
                ),
            ],
            options={
                "verbose_name": "operating hours",
                "verbose_name_plural": "operating hours",
                "ordering": ["day_of_week", "opens"],
            },
        ),
    ]
