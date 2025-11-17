from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, F
from django.utils import timezone
from .models import Venta, ItemVenta
from .forms import VentaForm, ItemVentaForm, ItemVentaFormSet
from productos.models import Producto

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.db import transaction

class VentaListView(ListView):
    model = Venta
    template_name = "ventas/venta_list.html"
    context_object_name = "ventas"
    #paginate_by = 


class VentaDetailView(DetailView):
    model = Venta
    template_name = "ventas/venta_detail.html"
    context_object_name = "venta"


class VentaCreateView(CreateView):
    model = Venta
    form_class = VentaForm
    template_name = "ventas/venta_form.html"
    success_url = reverse_lazy("ventas:venta_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["formset"] = ItemVentaFormSet(self.request.POST, prefix="items")
        else:
            context["formset"] = ItemVentaFormSet(prefix="items")

        productos = Producto.objects.all().values("id", "precio")
        context["productos_precios"] = {str(p["id"]): float(p["precio"]) for p in productos}

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        if not formset.is_valid():
            messages.error(self.request, "Hay errores en los items.")
            return self.form_invalid(form)

        try:
            with transaction.atomic():
                self.object = form.save()

                total = 0

                for item_form in formset:
                    data = item_form.cleaned_data
                
                    if not data or not data.get("producto"):
                        continue
                    
                    producto = data["producto"]
                    cantidad = data["cantidad"]
                    precio = producto.precio
                
                    if cantidad > producto.stock:
                        raise ValueError(...)
                
                    item = item_form.save(commit=False)
                    item.venta = self.object
                    item.precio_unitario = precio
                    item.subtotal = precio * cantidad
                    item.save()
                
                    producto.stock -= cantidad
                    producto.save()
                
                    total += item.subtotal
                
                self.object.total = total
                self.object.save()


                messages.success(self.request, "Venta registrada correctamente.")
                return redirect(self.success_url)

        except Exception as e:
            messages.error(self.request, f"Error al guardar la venta: {e}")
            return self.form_invalid(form)

"""
class VentaUpdateView(UpdateView):
    model = Venta
    template_name = "ventas/venta_form.html"
    success_url = reverse_lazy("ventas:venta_list")

    def form_valid(self, form):
        respone = super.form_valid(form)
        messages.success(self.request, "Venta actualizada exitosamente")
        return respone

class VentaDeleteView(DeleteView):
    model = Venta
    template_name = "ventas/venta_delete.html"
    context_object_name = "venta"
    success_url = reverse_lazy("ventas:venta_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Venta eliminada exitosamente")
        return super().delete(request, *args, **kwargs)

"""




