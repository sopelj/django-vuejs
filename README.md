# Django VueJS

Tools to help integrate vuejs into Django projects especially with regards to forms

## Installation

1. Add to your requirements or install via pip

   ```
   pip install git+https://github.com/sopelj/django-vuejs.git@version  # eg. @v0.1
   ```

2. To use template tags add to your projects `INSTALLED_APPS`

   ```python
   INSTALLED_APPS = [
       ...
       'django_vuejs',
       ...
   ]
   ```

## Forms

Create a form that uses the VueJsFormMixin

```python
from django import forms
from django_vuejs.forms import VueFormMixin
from .models import Example  

class ExampleForm(VueFormMixin, forms.ModelForm):
    class Meta:
        model = Example
```

If you wish to change the layout of your form you can override the form `template_name` and create your own

```python
from django import forms
from django_vuejs.forms import VueFormMixin
from .models import Example 

class ExampleForm(VueFormMixin, forms.ModelForm):
    template_name = 'myapp/example_form.html'
    
    class Meta:
        model = Example
```

This will create a form that binds the form fields to a prop called `form` and expects form errors to be in a prop called `errors`
This can be changed with the properties `form_prop_name` and `errors_prop_name`.

If you wish to use a Vue component for one of your fields you can override the widgets and use the `VueComponentWidget` or the `VueSelectWidget`.

```python
from django import forms
from django_vuejs.forms import VueFormMixin
from django_vuejs.widgets import VueComponentWidget, VueSelectWidget
from .models import Example 

class ExampleForm(VueFormMixin, forms.ModelForm):
    class Meta:
        model = Example
        widgets = {
            'phone': VueComponentWidget('phone-input'),
            'birth_date': VueComponentWidget('date-input'),
            'favourite_colour': VueSelectWidget('v-select'),
        }
```
