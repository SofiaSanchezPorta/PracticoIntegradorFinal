from django import forms
from django.forms import inlineformset_factory
from crispy_forms.layout import Layout, Row, Column, Field
from core.crispy import BaseFormHelper

from ventas.models import Venta, ItemVenta
from clientes.models import Cliente
from productos.models import Producto

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ["cliente"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.form_tag = False

        self.fields["cliente"].queryset = Cliente.objects.all()
        self.fields["cliente"].empty_label = "Seleccione un cliente"
        self.fields["cliente"].required = True

class ItemVentaForm(forms.ModelForm):
    class Meta:
        model = ItemVenta
        fields = ["producto", "cantidad", "precio_unitario", "subtotal"]
        widgets = {
            "producto": forms.Select(attrs={"class": "form-control"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "subtotal": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["producto"].required = True
        self.fields["cantidad"].required = True
        self.fields["precio_unitario"].required = False
        self.fields["subtotal"].required = False

    def clean(self):
        cleaned = super().clean()

        producto = cleaned.get("producto")
        cantidad = cleaned.get("cantidad")

        if not producto or not cantidad:
            return cleaned

        if cantidad > producto.stock:
            raise forms.ValidationError(
                f"Stock insuficiente: sólo hay {producto.stock} unidades disponibles."
            )

        cleaned["precio_unitario"] = producto.precio
        cleaned["subtotal"] = producto.precio * cantidad
        return cleaned

ItemVentaFormSet = inlineformset_factory(
    Venta,
    ItemVenta,
    form=ItemVentaForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
    fields=["producto", "cantidad", "precio_unitario", "subtotal"],
)
