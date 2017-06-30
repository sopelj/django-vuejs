from typing import Any, Dict, List, Union

from django import template
from rest_framework.renderers import JSONRenderer

register = template.Library()


@register.filter(name='json')
def as_json(data: Union[Dict, List]) -> str:
    return JSONRenderer().render(data)


@register.filter(name='str')
def as_str(value: Any) -> str:
    return str(value)
