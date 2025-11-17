from django import forms
#from django.core.exceptions import ValidationError
from .models import Venta, ItemVenta
from crispy_forms.layout import Layout, Row, Column, Submit, Reset, ButtonHolder, Field, Div, HTML
#from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
#from crispy_forms.helper import FormHelper
from core.crispy import BaseFormHelper
from django.forms import inlineformset_factory
from ventas.models import Venta, ItemVenta
from clientes.models import Cliente
from productos.models import Producto

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ["cliente"]
        widgets = {
            'cliente': forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.fields["cliente"].queryset = Cliente.objects.all()
        self.fields["cliente"].empty_label = "Seleccione un cliente"
        self.fields["cliente"].required = True
"""
class ItemVentaForm(forms.ModelForm):
    class Meta:
        model = ItemVenta
        fields = ["producto", "cantidad", "precio_unitario"]
        widgets = {
            "precio_unitario": forms.TextInput(
                attrs={
                    "placeholder": "Ej: 0.53",   # ponermos cualquier numero
                }
            )
        }
"""
class ItemVentaForm(forms.ModelForm):
    class Meta:
        model = ItemVenta
        fields = ["producto", "cantidad", "precio_unitario", "subtotal"]
        #PARA QUE NO SE PUEDA MODIFICAR EL PRECIO UNITARIO DEL PRODUCTO QUE TIENE ASIGNADO
        widgets = {
            "producto": forms.Select(attrs={"class": "form-control"}),
            #"precio_unitario": forms.NumberInput(attrs={"readonly": "readonly"}),
            #"subtotal": forms.NumberInput(attrs={"readonly": "readonly"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["producto"].required = True
        self.fields["cantidad"].required = True

        self.fields["precio_unitario"].required = False
        self.fields["subtotal"].required = False

        self.helper = BaseFormHelper()
        self.helper.layout = Layout(
            Row(
                Column(Field("producto"), css_class="col-md-4"),
                Column(Field("cantidad"), css_class="col-md-2"),
                Column(Field("precio_unitario"), css_class="col-md-3"),
                Column(Field("subtotal"), css_class="col-md-3"),
            )
        )

        if getattr(self.instance, "producto_id", None):
            self.fields["precio_unitario"].initial = self.instance.producto.precio

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get("producto")
        cantidad = cleaned_data.get("cantidad")

        if not producto or not cantidad:
            return cleaned_data

        if cantidad > producto.stock:
            raise forms.ValidationError(
                f"Stock insuficiente: sólo hay {producto.stock} unidades disponibles"
            )

        cleaned_data["precio_unitario"] = producto.precio
        cleaned_data["subtotal"] = producto.precio * cantidad

        return cleaned_data

        cleaned_data = super().clean()
        producto = cleaned_data.get("producto")
        cantidad = cleaned_data.get("cantidad")

        if producto and cantidad:
            if cantidad > producto.stock:
                raise forms.ValidationError(
                    f"Stock insuficiente: sólo hay {producto.stock} unidades disponibles"
                )

            cleaned_data["precio_unitario"] = producto.precio
            cleaned_data["subtotal"] = producto.precio * cantidad

            return cleaned_data

        cleaned_data = super().clean()
        producto = cleaned_data.get("producto")
        cantidad = cleaned_data.get("cantidad")

        if producto and cantidad:
            if cantidad > producto.stock:
                raise forms.ValidationError(
                    f"Stock insuficiente: sólo hay {producto.stock} unidades disponibles"
                )

            cleaned_data["precio_unitario"] = producto.precio
            cleaned_data["subtotal"] = producto.precio * cantidad

        return cleaned_data

ItemVentaFormSet = inlineformset_factory(
    Venta,
    ItemVenta,
    form=ItemVentaForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True,
    fields=['producto', 'cantidad', 'precio_unitario', "subtotal"],
    validate_max=False,  # No límite máximo
)