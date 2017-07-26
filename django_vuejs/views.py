from typing import Optional, Dict, Union, Any

from django.db.models import Model
from django.forms import ModelForm
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import list_route

from .forms import VueFormMixin


class VueFormAPIViewSet(ModelViewSet):
    """
    API View to allow fetching instance as well as creation and update of model instance via a form
    """
    form_class: type(VueFormMixin) = None

    def get_form_kwargs(self, instance: Optional[Model] = None) -> dict:
        """
        Method to allow you to pass custom parameters to form init
        """
        return {'instance': instance} if instance else {}

    def get_initial_form_data(self) -> dict:
        """
        Return initial form values if no instance is bound to form
        """
        return {}

    def get_form(self, instance: Optional[Model] = None) -> VueFormMixin:
        """
        Return a form instance. Bound only if posting data
        """
        form_kwargs = self.get_form_kwargs(instance)
        form_class = self.get_form_class()
        if self.request.method == 'POST' and self.request.data:
            return form_class(self.request.data, **form_kwargs)
        return form_class(**form_kwargs)

    def get_form_class(self) -> type(VueFormMixin):
        """
        Allow one to override form_class
        """
        return self.form_class

    def retrieve(self, request, *args, **kwargs) -> Response:
        """
        Fetch object data as represented in the form
        Passing the option `include_component=true` via get will also return the component with with the form template
        """
        instance = self.get_object()
        include_component = request.GET.get('include_component') == 'true'
        return Response(self.get_form_response(self.get_form(instance), include_component))

    def get_form_response(self, form: Optional[VueFormMixin] = None, include_component: bool = False) -> dict:
        """
        Extract errors and form_data from form or return defaults
        """
        errors = {}
        if form is not None and (form.is_bound or (isinstance(form, ModelForm) and form.instance.pk)):
            data = form.get_serialized_form_data()
        else:
            data = self.get_initial_form_data()

        if form is not None and form.is_bound:
            form.is_valid()
            errors = form.errors

        response = {'form_data': data, 'errors': errors}
        if include_component is True:
            response['form_component'] = self.get_form_component()
        return response

    def get_form_component(self) -> Dict[str, Any]:
        """
        Get form template and props
        """
        form = self.get_form_class()(**self.get_form_kwargs())
        return {
            'template': str(form),  # renders form.template_name
            'props': [form.form_prop_name, form.errors_prop_name],
        }

    @list_route(methods=['get'], url_path='form-component')
    def retrieve_form_component(self, request: Request, *args, **kwargs) -> Response:
        """
        Fetch form as a dynamic component that can be bound to <component>

        this.formComponent = response.data
        this.formData = {}
        this.formErrors = {}

        <keep-alive>
            <component :is="formComponent" :form="formData" :errors="formErrors"></component>
        </keep-alive>
        """
        return Response(self.get_form_response(include_component=True))

    def save_form(self, form: VueFormMixin):
        """
        Hook to change instance pre/post save
        """
        return form.save()

    def form_valid(self, form: VueFormMixin):
        """
        Hook for valid form response
        """
        creating = not form.instance.pk
        self.save_form(form)
        response_data = self.get_form_response(form)
        return Response(response_data, status=201 if creating else 200)

    def form_invalid(self, form: VueFormMixin):
        """
        Hook for invalid form response
        """
        return Response(self.get_form_response(form), status=400)

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Use form to validate model before creation
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """
        Use form to validate model for update
        """
        form = self.get_form(self.get_object())
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)
