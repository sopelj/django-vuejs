import json
from typing import Any, Dict

from django.db.models import Model
from django.forms import BaseForm, MultiWidget, Select, SelectMultiple
from django.template.loader import render_to_string
from rest_framework.utils.encoders import JSONEncoder

from .widgets import VueSelectWidget


class VueFormMixin(BaseForm):
    """
    Form that facilitates returning data as json and can be coerced into a string for inclusion in components
    """
    ignored_fields = tuple()
    form_prop_name = 'form'
    errors_prop_name = 'errors'
    template_name = 'vuejs/form.html'

    def __init__(self, *args, **kwargs):
        """
        Update field widgets unless ignored
        """
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            if field_name not in self.ignored_fields:
                self.vueify_field_widget(field_name)

    def vueify_field_widget(self, field_name: str) -> None:
        """
        Add v-model to field by name.
        Some fields need to be converted to different widgets to work such as select and multiwidgets
        """
        widget = self.fields[field_name].widget

        if isinstance(widget, MultiWidget):
            for i, sub_widget in enumerate(widget.widgets):
                sub_widget.attrs['v-model'] = f'{self.form_prop_name}.{field_name}_{i}'
        else:
            if widget.__class__ in [Select, SelectMultiple]:
                if isinstance(widget, SelectMultiple):
                    self.fields[field_name].widget.attrs['multiple'] = True
                self.fields[field_name].widget.__class__ = VueSelectWidget
                self.fields[field_name].widget.attrs[':value'] = f'{self.form_prop_name}.{field_name}'

            self.fields[field_name].widget.attrs.update({
                'v-model': f'form.{field_name}',
            })

    def get_serialized_form_data(self) -> Dict[str, Any]:
        """
        Get cleaned data as a dictionary that can be safely converted to JSON
        """
        if not self.is_bound:
            return {}

        data = {}
        if not hasattr(self, 'cleaned_data'):
            self.is_valid()

        for field_name, field in self.fields.items():
            value = self.cleaned_data.get(field_name)
            if not value:
                continue

            if isinstance(field.widget, MultiWidget):
                try:
                    values = json.loads(value)
                    for i, _ in enumerate(field.widget.widgets):
                        data[f'{field_name}_{i}'] = values[i]
                except (json.JSONDecodeError, KeyError):
                    pass
            else:
                data[field_name] = value.pk if isinstance(value, Model) else value
        return json.loads(JSONEncoder().encode(data))

    def __str__(self) -> str:
        """
        Render this forms template when converted to string
        """
        return render_to_string(self.template_name, {self.form_prop_name: self})
