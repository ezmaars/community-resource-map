"""Views for the public site and the staff moderation queue."""

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _

from .forms import ResourceSubmitForm
from .models import Category, Resource, Tag
from .utils import filter_open_now


def _apply_filters(request):
    """Build an approved-resource queryset from the request's query params."""
    qs = Resource.objects.approved().select_related("category").prefetch_related("tags")

    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    free = request.GET.get("free") in ("1", "true", "on")
    tag_slugs = [t for t in request.GET.getlist("tag") if t]

    qs = qs.search(query)
    if category:
        qs = qs.filter(category__slug=category)
    if free:
        qs = qs.free_only()
    for slug in tag_slugs:
        qs = qs.filter(tags__slug=slug)

    return qs.distinct(), {
        "q": query,
        "category": category,
        "free": free,
        "tags": tag_slugs,
        "open_now": request.GET.get("open") in ("1", "true", "on"),
    }


def home(request):
    """Landing page: hero search, category grid, recently added resources."""
    context = {
        "categories": Category.objects.all(),
        "recent": Resource.objects.approved().select_related("category")[:6],
        "total": Resource.objects.approved().count(),
    }
    return render(request, "home.html", context)


def browse(request):
    """Map + list view with search and filters."""
    qs, active = _apply_filters(request)

    resources = list(qs)
    if active["open_now"]:
        resources = filter_open_now(resources)

    context = {
        "resources": resources,
        "count": len(resources),
        "categories": Category.objects.all(),
        "tags": Tag.objects.all(),
        "active": active,
        # Pass the raw query string (minus page noise) so map.js can call the API.
        "query_string": request.GET.urlencode(),
    }
    return render(request, "resources/browse.html", context)


def resource_detail(request, slug):
    """Single resource page. Pending items are visible only to staff."""
    resource = get_object_or_404(
        Resource.objects.select_related("category").prefetch_related("tags", "opening_hours"),
        slug=slug,
    )
    if not resource.is_approved and not request.user.is_staff:
        # Hide unapproved resources from the public.
        from django.http import Http404

        raise Http404("Resource not found")
    return render(request, "resources/detail.html", {"resource": resource})


def submit(request):
    """Public submit-a-resource form. Saves as PENDING for moderation."""
    if request.method == "POST":
        form = ResourceSubmitForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.status = Resource.Status.PENDING
            resource.verification = Resource.Verification.UNVERIFIED
            if request.user.is_authenticated:
                resource.submitted_by = request.user
            resource.save()
            form.save_m2m()
            return redirect("submit_success")
    else:
        form = ResourceSubmitForm()
    return render(request, "resources/submit.html", {"form": form})


def submit_success(request):
    return render(request, "resources/submit_success.html")


# -----------------------------------------------------------------------------
# Staff moderation queue (a lightweight complement to the Django admin)
# -----------------------------------------------------------------------------
@staff_member_required
def manage_queue(request):
    """List pending submissions with one-click approve/reject."""
    if request.method == "POST":
        resource = get_object_or_404(Resource, pk=request.POST.get("resource_id"))
        action = request.POST.get("action")
        notes = request.POST.get("review_notes", "").strip()

        if action == "approve":
            resource.status = Resource.Status.APPROVED
            resource.verification = Resource.Verification.VERIFIED
            messages.success(request, _("Approved: %(name)s") % {"name": resource.name})
        elif action == "reject":
            resource.status = Resource.Status.REJECTED
            messages.info(request, _("Rejected: %(name)s") % {"name": resource.name})
        else:
            messages.error(request, _("Unknown action."))
            return redirect("manage_queue")

        resource.review_notes = notes
        resource.reviewed_by = request.user
        resource.reviewed_at = timezone.now()
        resource.save()
        return redirect("manage_queue")

    pending = (
        Resource.objects.pending().select_related("category").order_by("created_at")
    )
    return render(
        request,
        "manage/queue.html",
        {"pending": pending, "pending_count": pending.count()},
    )


# -----------------------------------------------------------------------------
# Error handlers
# -----------------------------------------------------------------------------
def handler404(request, exception):
    return render(request, "404.html", status=404)


def handler500(request):
    return render(request, "500.html", status=500)
