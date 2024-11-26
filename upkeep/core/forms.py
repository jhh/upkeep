from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Button, Div, Field, Layout, Submit
from django import forms
from django.urls import reverse

from upkeep.core.models import Area


class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ["name", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_edit = self.instance.id is not None

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = (
            reverse("area", args=[self.instance.id]) if is_edit else reverse("areas")
        )

        self.helper.layout = Layout(
            Field("name", css_class="textinput form-control"),
            Field("notes", css_class="textarea form-control"),
            Div(
                Submit(
                    "submit",
                    "Update" if is_edit else "Save",
                    css_class="btn btn-primary",
                ),
                Button(
                    "cancel",
                    "Cancel",
                    css_class="btn btn-secondary ms-2",
                    onclick="window.history.back();",
                ),
                HTML(f"""<button class="btn btn-outline-danger ms-auto"
                hx-delete="{{% url 'area' {self.instance.id} %}}"
                hx-confirm="Delete this area and all of its tasks?"
                >Delete</button>""")
                if is_edit
                else None,
                css_class="d-flex",
            ),
        )
