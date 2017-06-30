from typing import Optional

from django.forms import Select, Widget
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from rest_framework.utils.encoders import JSONEncoder


class VueComponentWidget(Widget):
    """
    Widget that allows you to set a form field to a vue js component

    ex. widgets = {'phone': VueComponentWidget('phone-input')}
    """
    default_component_name = 'input'

    def __init__(self, component_name: Optional[str], **kwargs):
        self.component_name = component_name or self.default_component_name
        super().__init__(**kwargs)

    def render(self, name, value, attrs=None, **kwargs):
        if not attrs:
            attrs = {}
        attrs['name'] = name
        if 'value' not in attrs:
            attrs['value'] = value or ''
        field = f'<{self.component_name} {flatatt(attrs)}>'
        if self.component_name != 'input':
            field += f'</{self.component_name}>'
        return mark_safe(field)


class VueSelectWidget(Select, VueComponentWidget):
    default_component_name = 'v-select'
    choice_id_key = 'value'
    choice_label_key = 'label'

    def render(self, name, value, attrs=None, **kwargs):
        if not attrs:
            attrs = {}
        attrs.update({
            'name': name,
            ':options': JSONEncoder().encode([
                {
                    self.choice_id_key: str(choice),
                    self.choice_label_key: str(label).replace("'", "’")
                }
                for choice, label in self.choices
            ]),
        })
        return super().render(name, value, attrs, **kwargs)
