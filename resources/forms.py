"""Forms for public resource submission."""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Resource, Tag


class ResourceSubmitForm(forms.ModelForm):
    """
    Form shown to the public on /submit/.

    New submissions are always saved with status=PENDING (set in the view),
    so nothing appears on the map until a moderator approves it.
    """

    # Honeypot: real users never see or fill this. Bots usually do.
    # If it contains anything, we silently reject the submission.
    company = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "tabindex": "-1",
                "autocomplete": "off",
                "aria-hidden": "true",
                "class": "visually-hidden",
            }
        ),
        label="",
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label=_("Features"),
    )

    class Meta:
        model = Resource
        fields = [
            "name",
            "category",
            "description",
            "address",
            "city",
            "state",
            "postal_code",
            "latitude",
            "longitude",
            "service_area",
            "phone",
            "email",
            "website",
            "hours_note",
            "is_free",
            "cost_notes",
            "tags",
            "submitter_name",
            "submitter_email",
        ]
        labels = {
            "name": _("Organization or service name"),
            "hours_note": _("Hours"),
            "is_free": _("This service is free"),
            "submitter_name": _("Your name (optional)"),
            "submitter_email": _("Your email (optional)"),
        }
        help_texts = {
            "latitude": _("Optional. Helps place the pin precisely."),
            "longitude": _("Optional."),
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "service_area": forms.TextInput(),
            "cost_notes": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Bootstrap classes consistently without repeating them above.
        for name, field in self.fields.items():
            if name == "company":
                continue
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.CheckboxSelectMultiple):
                pass  # rendered manually in the template
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")

    def clean_company(self):
        # Honeypot must stay empty.
        if self.cleaned_data.get("company"):
            raise forms.ValidationError("Spam detected.")
        return ""

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get("latitude")
        lng = cleaned.get("longitude")
        # Require either a usable address or coordinates so the resource is findable.
        if not (cleaned.get("address") or cleaned.get("city")) and lat is None:
            raise forms.ValidationError(
                _("Please provide an address/city or map coordinates so people can find this.")
            )
        if lat is not None and not (-90 <= lat <= 90):
            self.add_error("latitude", _("Latitude must be between -90 and 90."))
        if lng is not None and not (-180 <= lng <= 180):
            self.add_error("longitude", _("Longitude must be between -180 and 180."))
        return cleaned
