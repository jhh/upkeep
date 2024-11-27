from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field, Layout, Submit
from django import forms
from django.urls import reverse

from upkeep.core.models import Area, Consumable, Schedule, Task


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
            Field("name", css_class="form-control"),
            Field("notes", css_class="form-control"),
            Div(
                Submit(
                    "submit",
                    "Update" if is_edit else "Save",
                    css_class="btn btn-primary",
                ),
                StrictButton(
                    "Cancel",
                    name="cancel",
                    css_class="btn-secondary ms-2",
                    onclick="window.history.back();",
                ),
                HTML(f"""<button type="button" class="btn btn-outline-danger ms-auto"
                hx-delete="{{% url 'area' {self.instance.id} %}}"
                hx-confirm="Delete this area and all of its tasks?"
                >Delete</button>""")
                if is_edit
                else None,
                css_class="d-flex",
            ),
        )


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["area", "name", "interval", "frequency", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_edit = self.instance.id is not None
        for field in ("interval", "frequency"):
            self.fields[field].label = None

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = (
            reverse("task_edit", args=[self.instance.id]) if is_edit else reverse("tasks")
        )

        self.helper.layout = Layout(
            Field("name", css_class="form-control"),
            Field("area", css_class="form-control"),
            Div(
                Div(
                    Field("interval", css_class="form-control", placeholder="interval"),
                    css_class="col",
                ),
                Div(Field("frequency", css_class="form-control"), css_class="col"),
                css_class="row",
            ),
            Field("duration", css_class="form-control"),
            Field("notes", css_class="form-control"),
            Div(
                Submit(
                    "submit",
                    "Update" if is_edit else "Save",
                    css_class="btn btn-primary",
                ),
                StrictButton(
                    "Cancel",
                    name="cancel",
                    css_class="btn-secondary ms-2",
                    onclick="window.history.back();",
                ),
                HTML(f"""<button type="button" class="btn btn-outline-danger ms-auto"
                hx-delete="{{% url 'task_edit' {self.instance.id} %}}"
                hx-confirm="Delete this task?"
                >Delete</button>""")
                if is_edit
                else None,
                css_class="d-flex",
            ),
        )


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ["task", "due_date", "completion_date", "notes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_edit = self.instance.id is not None

        self.helper = FormHelper()
        self.helper.render_hidden_fields = True
        self.helper.form_method = "post"
        self.helper.form_action = (
            reverse("schedule_edit", args=[self.instance.id])
            if is_edit
            else reverse("schedule_new")
        )

        tasks = Task.objects.select_related().values_list("id", "area__name", "name")
        self.fields["task"].choices = [(t[0], f"{t[1]}: {t[2]}") for t in tasks]  # type: ignore

        self.helper.layout = Layout(
            Field("task"),
            Field("due_date", css_class="form-control"),
            Field("completion_date", css_class="form-control"),
            Field("notes", css_class="form-control"),
            Div(
                Submit(
                    "submit",
                    "Update" if is_edit else "Save",
                    css_class="btn btn-primary",
                ),
                StrictButton(
                    "Cancel",
                    name="cancel",
                    css_class="btn-secondary ms-2",
                    onclick="window.history.back();",
                ),
                HTML(f"""<button type="button" class="btn btn-outline-danger ms-auto"
                hx-delete="{{% url 'schedule_edit' {self.instance.id} %}}"
                hx-confirm="Delete this schedule?"
                >Delete</button>""")
                if is_edit
                else None,
                css_class="d-flex",
            ),
        )


class ConsumableForm(forms.ModelForm):
    class Meta:
        model = Consumable
        fields = ["name", "notes", "quantity", "unit"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        is_edit = self.instance.id is not None

        self.helper = FormHelper()
        self.helper.render_hidden_fields = True
        self.helper.form_method = "post"
        self.helper.form_action = (
            reverse("consumable_edit", args=[self.instance.id])
            if is_edit
            else reverse("consumable_new")
        )

        self.helper.layout = Layout(
            Field("name", css_class="form-control"),
            Field("quantity", css_class="form-control"),
            Field("unit", css_class="form-control"),
            Field("notes", css_class="form-control"),
            Div(
                Submit(
                    "submit",
                    "Update" if is_edit else "Save",
                    css_class="btn btn-primary",
                ),
                StrictButton(
                    "Cancel",
                    name="cancel",
                    css_class="btn-secondary ms-2",
                    onclick="window.history.back();",
                ),
                HTML(f"""<button type="button" class="btn btn-outline-danger ms-auto"
                hx-delete="{{% url 'consumable_edit' {self.instance.id} %}}"
                hx-confirm="Delete this consumable?"
                >Delete</button>""")
                if is_edit
                else None,
                css_class="d-flex",
            ),
        )
