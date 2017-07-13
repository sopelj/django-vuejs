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
        final_attrs = self.build_attrs(attrs)
        final_attrs['name'] = name
        if 'value' not in final_attrs:
            final_attrs['value'] = value or ''
        field = f'<{self.component_name} {flatatt(final_attrs)}>'
        if self.component_name != 'input':
            field += f'</{self.component_name}>'
        return mark_safe(field)


class VueSelectWidget(Select):
    default_component_name = 'v-select'
    choice_id_key = 'value'
    choice_label_key = 'label'

    def __init__(self, component_name: Optional[str]=None, multiple: bool=False, **kwargs):
        self.component_name = component_name or self.default_component_name
        super().__init__(**kwargs)
        self.multiple = multiple

    def value_from_datadict(self, data, files, name):
        if self.multiple:
            return data.getlist(name)
        return data.get(name)

    def value_omitted_from_data(self, data, files, name):
        if self.multiple:
            return False
        return super().value_omitted_from_data(data, files, name)

    def render(self, name, value, attrs=None, **kwargs):
        final_attrs = self.build_attrs(attrs)
        value_attr = ':value' if self.multiple else 'value'
        default_value = '[]' if self.multiple else ''
        if value_attr not in final_attrs:
            final_attrs[value_attr] = value or default_value

        if self.multiple:
            final_attrs['multiple'] = True

        final_attrs.update({
            'name': name,
            ':options': JSONEncoder().encode([
                {
                    self.choice_id_key: choice,
                    self.choice_label_key: str(label).replace("'", "’")
                }
                for choice, label in self.choices
            ])
        })
        return mark_safe(f'<{self.component_name} {flatatt(final_attrs)}></{self.component_name}>')
