from typing import Optional

from django.db.models import Model
from rest_framework import generics, mixins
from rest_framework.request import Request
from rest_framework.response import Response

from .forms import VueFormMixin


class VueFormAPIView(mixins.CreateModelMixin, generics.RetrieveUpdateAPIView):
    """
    API View to allow fething instance as well as creation and update of model instance via a form
    """
    form_class: type(VueFormMixin) = None

    def get_form(self, instance: Optional[Model] = None) -> VueFormMixin:
        """
        Return a form instance. Bound only if posting data
        """
        form_kwargs = {'instance': instance} if instance else {}
        if self.request.method == 'POST' and self.request.data:
            return self.form_class(self.request.data, **form_kwargs)
        return self.form_class(**form_kwargs)

    def retrieve_form_component(self) -> Response:
        """
        Fetch form as a dynamic component that can be bound to <component>

        this.formComponent = response.data
        this.formData = {}
        this.formErrors = {}

        <keep-alive>
            <component :is="formComponent" :form="formData" :errors="formErrors"></component>
        </keep-alive>
        """
        form = self.form_class()
        return Response({
            'template': str(form),  # renders form.template_name
            'props': [
                form.form_prop_name,
                form.errors_prop_name,
            ],
        })

    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Use form to validate model before creation
        """
        form = self.get_form()
        if form.is_valid():
            instance = form.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=201)
        return Response({'errors': form.errors}, status=400)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """
        Use form to validate model for update
        """
        form = self.get_form(self.get_object())
        if form.is_valid():
            instance = form.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=200)
        return Response({'errors': form.errors}, status=400)
