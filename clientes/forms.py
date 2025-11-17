from django import forms
from django.core.exceptions import ValidationError
from .models import Cliente
from crispy_forms.layout import Layout, Row, Column, Submit, Reset, ButtonHolder, Field, Div, HTML
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from crispy_forms.helper import FormHelper
from core.crispy import BaseFormHelper

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "apellido", "dni", "telefono", "mail"]
        help_texts = {
            "dni": "Ingrese el número sin puntos",
            "telefono": "Ingrese el número sin puntos. Hasta 13 dígitos"
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = BaseFormHelper()

        self.helper.layout = Layout(
            Field("nombre"),
            Field("apellido"),
            Field("dni", placeholder = "12345678"),
            Field("telefono", placeholder = "0351153555777"),
            Field("mail"),
            ButtonHolder(
                Submit("submit", "Guardar", css_class="btn btn-success"),
                Reset("reset", "Limpiar", css_class="btn btn-outline-secondary"),
                HTML('<a href="{% url \'clientes:cliente_list\' %}" class="btn btn-secondary">Cancelar</a>')
            )
        )

    def clean_dni(self):
        dni = self.cleaned_data.get("dni")
        
        if not str(dni).isdigit():
            raise ValidationError("El DNI debe contener solo números.")
        
        dni = int(dni)

        if dni <= 0:
            raise ValidationError("El DNI debe ser mayor a cero.")

        if dni > 50000000:
            raise ValidationError("El DNI no puede ser mayor a 50 millones.")
        
        return dni
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")
        
        if not str(telefono).isdigit():
            raise ValidationError("El teléfono debe contener solo números.")
        
        if len(str(telefono)) > 13:
            raise ValidationError("El teléfono no puede tener más de 13 dígitos.")
        return telefono
    