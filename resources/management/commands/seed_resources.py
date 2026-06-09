"""
Load sample data so the map is populated on first run.

Usage:
    python manage.py seed_resources          # add data (idempotent-ish)
    python manage.py seed_resources --flush   # delete existing resources first

All sample resources are fictional but use real coordinates around downtown
Denver, CO so the map looks realistic out of the box. Edit MAP_DEFAULT_* in
.env to recenter for your own community.
"""

from datetime import time

from django.core.management.base import BaseCommand
from django.db import transaction

from resources.models import Category, OperatingHours, Resource, Tag

CATEGORIES = [
    ("Food", "🍎", "#d9534f", "Food banks, pantries, and free meals"),
    ("Housing", "🏠", "#5b8def", "Shelters, transitional housing, and rent help"),
    ("Health", "➕", "#2f7d5b", "Free and low-cost clinics and mental health"),
    ("Legal", "⚖️", "#7a5bd0", "Free legal aid and advice"),
    ("Education", "📚", "#e0922f", "Free classes, tutoring, and literacy"),
    ("Jobs", "💼", "#1f9bb3", "Job training and employment support"),
    ("Emergency", "🚨", "#c0392b", "Crisis lines and emergency assistance"),
]

TAGS = [
    "Wheelchair accessible",
    "Family friendly",
    "Multilingual",
    "Walk-in",
    "Appointment required",
    "No ID required",
]

# (name, category, description, address, city, lat, lng, tags, hours_note, is_free, hours)
RESOURCES = [
    (
        "Eastside Community Food Bank",
        "Food",
        "Free groceries and fresh produce for anyone in need. No ID required.",
        "1420 Welton St", "Denver", 39.7460, -104.9870,
        ["Walk-in", "No ID required", "Multilingual"],
        "Mon–Sat 9am–4pm", True,
        [(d, time(9, 0), time(16, 0)) for d in range(0, 6)],
    ),
    (
        "Hope Kitchen Free Meals",
        "Food",
        "Hot meals served daily, no questions asked. Vegetarian options available.",
        "2100 Larimer St", "Denver", 39.7556, -104.9897,
        ["Walk-in", "Family friendly"],
        "Daily 11am–1pm and 5pm–7pm", True,
        [(d, time(11, 0), time(13, 0)) for d in range(0, 7)],
    ),
    (
        "Riverside Emergency Shelter",
        "Housing",
        "Overnight shelter beds for adults. Intake begins at 6pm; arrive early.",
        "850 S Federal Blvd", "Denver", 39.7100, -105.0260,
        ["Walk-in", "Wheelchair accessible"],
        "Intake 6pm–9pm nightly", True,
        [(d, time(18, 0), time(21, 0)) for d in range(0, 7)],
    ),
    (
        "New Start Rental Assistance",
        "Housing",
        "Help with overdue rent and utilities to prevent eviction. By appointment.",
        "303 Park Ave W", "Denver", 39.7570, -104.9810,
        ["Appointment required", "Multilingual"],
        "Mon–Fri 9am–5pm by appointment", True,
        [(d, time(9, 0), time(17, 0)) for d in range(0, 5)],
    ),
    (
        "Downtown Free Health Clinic",
        "Health",
        "Free primary care, vaccinations, and basic dental. Sliding scale for labs.",
        "660 Bannock St", "Denver", 39.7290, -104.9890,
        ["Wheelchair accessible", "Multilingual", "Appointment required"],
        "Mon–Thu 8am–6pm, Fri 8am–noon", True,
        [(d, time(8, 0), time(18, 0)) for d in range(0, 4)] + [(4, time(8, 0), time(12, 0))],
    ),
    (
        "Community Mental Health Drop-In",
        "Health",
        "Free counseling and peer support groups. Walk-ins welcome.",
        "1290 Williams St", "Denver", 39.7370, -104.9650,
        ["Walk-in", "Family friendly"],
        "Tue–Sat 10am–7pm", True,
        [(d, time(10, 0), time(19, 0)) for d in range(1, 6)],
    ),
    (
        "Justice for All Legal Aid",
        "Legal",
        "Free legal advice on housing, immigration, and benefits. Interpreters available.",
        "1905 Sherman St", "Denver", 39.7430, -104.9840,
        ["Appointment required", "Multilingual", "Wheelchair accessible"],
        "Mon–Fri 9am–4pm", True,
        [(d, time(9, 0), time(16, 0)) for d in range(0, 5)],
    ),
    (
        "Tenant Rights Walk-In Clinic",
        "Legal",
        "Know your rights as a renter. Free 20-minute consultations, first-come first-served.",
        "1515 Arapahoe St", "Denver", 39.7480, -104.9990,
        ["Walk-in"],
        "Wednesdays 1pm–5pm", True,
        [(2, time(13, 0), time(17, 0))],
    ),
    (
        "Public Library Adult Learning Center",
        "Education",
        "Free GED prep, ESL classes, and computer skills. All levels welcome.",
        "10 W 14th Ave Pkwy", "Denver", 39.7375, -104.9905,
        ["Wheelchair accessible", "Multilingual", "Family friendly"],
        "Mon–Sat 10am–6pm", True,
        [(d, time(10, 0), time(18, 0)) for d in range(0, 6)],
    ),
    (
        "Kids After-School Tutoring",
        "Education",
        "Free homework help and reading support for K–8 students.",
        "3540 W 32nd Ave", "Denver", 39.7620, -105.0340,
        ["Family friendly", "Multilingual"],
        "School days 3pm–6pm", True,
        [(d, time(15, 0), time(18, 0)) for d in range(0, 5)],
    ),
    (
        "WorkReady Job Center",
        "Jobs",
        "Free resume help, interview coaching, and job placement services.",
        "1391 Speer Blvd", "Denver", 39.7330, -104.9990,
        ["Wheelchair accessible", "Appointment required"],
        "Mon–Fri 8:30am–4:30pm", True,
        [(d, time(8, 30), time(16, 30)) for d in range(0, 5)],
    ),
    (
        "Skilled Trades Training Program",
        "Jobs",
        "Free entry-level training in construction and electrical trades.",
        "4890 Brighton Blvd", "Denver", 39.7790, -104.9620,
        ["Appointment required"],
        "Info sessions Mon & Thu 10am", True,
        [(0, time(10, 0), time(11, 0)), (3, time(10, 0), time(11, 0))],
    ),
    (
        "24/7 Crisis & Suicide Lifeline (Local)",
        "Emergency",
        "Free, confidential support any time, day or night. Phone and walk-in.",
        "777 Bannock St", "Denver", 39.7270, -104.9885,
        ["Walk-in", "Multilingual", "No ID required"],
        "Open 24 hours", True,
        [(d, time(0, 0), time(23, 59)) for d in range(0, 7)],
    ),
    (
        "Cold Weather Warming Center",
        "Emergency",
        "Emergency overnight warming shelter activated during freezing weather.",
        "2301 Lawrence St", "Denver", 39.7560, -104.9830,
        ["Walk-in", "Wheelchair accessible"],
        "Activates below 20°F, 7pm–7am", True,
        [],
    ),
]


class Command(BaseCommand):
    help = "Load sample categories, tags, and resources."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing resources before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            Resource.objects.all().delete()
            self.stdout.write(self.style.WARNING("Deleted existing resources."))

        cats = {}
        for order, (name, icon, color, desc) in enumerate(CATEGORIES):
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={"icon": icon, "color": color, "description": desc, "order": order},
            )
            cats[name] = cat

        tags = {name: Tag.objects.get_or_create(name=name)[0] for name in TAGS}

        created = 0
        for row in RESOURCES:
            (
                name, cat_name, desc, address, city, lat, lng,
                tag_names, hours_note, is_free, hours,
            ) = row

            if Resource.objects.filter(name=name).exists():
                continue

            resource = Resource.objects.create(
                name=name,
                category=cats[cat_name],
                description=desc,
                address=address,
                city=city,
                state="CO",
                country="USA",
                latitude=lat,
                longitude=lng,
                service_area="Open to all",
                hours_note=hours_note,
                is_free=is_free,
                status=Resource.Status.APPROVED,
                verification=Resource.Verification.VERIFIED,
            )
            resource.tags.set([tags[t] for t in tag_names])
            for day, opens, closes in hours:
                OperatingHours.objects.create(
                    resource=resource, day_of_week=day, opens=opens, closes=closes
                )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {len(cats)} categories, {len(tags)} tags, "
                f"{created} new resources."
            )
        )
