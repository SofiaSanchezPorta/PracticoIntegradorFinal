from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q, F
from django.utils import timezone
from .models import Producto, MovimientoStock
from .forms import ProductoForm, MovimientoStockForm, AjusteStockForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models.deletion import ProtectedError

class ProductoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Producto
    template_name = "productos/producto_list.html"
    context_object_name = "productos"
    login_url = 'account_login'
    paginate_by = 5

    permission_required = "productos.view_producto"

    def has_permission(self):
        user = self.request.user

        if not super().has_permission():
            return False

        if user.is_superuser:
            return True
                
        return (super().has_permission() and self.request.user.groups.filter(name__in=["stock", "administradores"]).exists())

    def get_queryset(self):
        queryset = super().get_queryset()

        stock_bajo = self.request.GET.get('stock_bajo')
        if stock_bajo:
            queryset = queryset.filter(stock__lt=F("stock_minimo")) #EL FILTRO TOMA EL VALOR DE CAMPO STOCK_MINIMO Y DEVUELE LOS QUE ESTÁN POR DEBAJO
        return queryset.order_by("nombre")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stock_bajo'] = self.request.GET.get("stock_bajo")
        return context
    
class ProductoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Producto
    template_name = "productos/producto_detail.html"
    context_object_name = "producto"
    login_url = 'account_login'

    permission_required = "productos.view_producto"

    def has_permission(self):
        user = self.request.user

        if not super().has_permission():
            return False

        if user.is_superuser:
            return True
                
        return (super().has_permission() and self.request.user.groups.filter(name__in=["stock", "administradores"]).exists())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["movimientos"] = self.object.movimientos.all()[:10]
        context["form_ajuste"] = AjusteStockForm
        return context
    
#AGREGAR MIXIN LOGUIN REQUIREN DONDE CORRESPONDA
class ProductoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = "productos/producto_form.html"
    success_url = reverse_lazy("productos:producto_list")
    login_url = 'account_login'

    permission_required = "productos.add_producto"

    def has_permission(self):
        user = self.request.user

        if not super().has_permission():
            return False

        if user.is_superuser:
            return True
                
        return (super().has_permission() and self.request.user.groups.filter(name__in=["stock", "administradores"]).exists())

    def form_valid(self, form): #SE IMPLEMENTA CUANDO TENEMOS UNA VISTA ASOCIADA A UN FORMULARIO 
        response = super().form_valid(form)

        if form.cleaned_data["stock"] > 0:
            MovimientoStock.objects.create(
                producto= self.object,
                tipo="entrada",
                cantidad=form.cleaned_data["stock"],
                motivo = "Stock inicial",
                fecha = timezone.now(),
                usuario = self.request.user.username
            )

        messages.success(self.request, "Producto creado exitosamente")
        return response
    

class ProductoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Producto
    template_name = "productos/producto_form.html"
    form_class = ProductoForm
    success_url = reverse_lazy("productos:producto_list")
    login_url = 'account_login'

    permission_required = "productos.change_producto"

    def has_permission(self):
        user = self.request.user

        if not super().has_permission():
            return False

        if user.is_superuser:
            return True
                
        return (super().has_permission() and self.request.user.groups.filter(name__in=["stock", "administradores"]).exists())

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Producto actualizado exitosamente")
        return response
    

class ProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Producto
    template_name = "productos/producto_delete.html"
    success_url = reverse_lazy("productos:producto_list")
    login_url = 'account_login'

    permission_required = "productos.delete_producto"

    def post(self, request, *args, **kwargs):
            self.object = self.get_object()
            try:
                return super().post(request, *args, **kwargs)
            except ProtectedError:
                messages.error(
                    request,
                    "No se puede eliminar el producto porque tiene ventas asociadas."
                )
                return redirect("productos:producto_detail", pk=self.object.pk)
"""
    def has_permission(self):
        user = self.request.user

        if not super().has_permission():
            return False

        if user.is_superuser:
            return True
                
        return (super().has_permission() and self.request.user.groups.filter(name__in=["stock", "administradores"]).exists())

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Producto eliminado exitosamente")
        return super().delete(request, *args, **kwargs)
    """

class MovimientoStockCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = MovimientoStock
    template_name = "productos/movimiento_form.html"
    form_class = MovimientoStockForm
    login_url = 'account_login'

    permission_required = "productos.add_movimientostock"

    def has_permission(self):
        user = self.request.user

        if not super().has_permission():
            return False

        if user.is_superuser:
            return True
                
        return (super().has_permission() and self.request.user.groups.filter(name__in=["stock", "administradores"]).exists())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["producto"] = get_object_or_404(Producto, pk=self.kwargs["pk"])
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["producto"] = get_object_or_404(Producto, pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        movimiento = form.save(commit=False)
        movimiento.producto = get_object_or_404(Producto, pk=self.kwargs["pk"])
        movimiento.usuario = self.request.user.username

        if movimiento.tipo == "entrada":
            movimiento.producto.stock +=movimiento.cantidad
        elif movimiento.tipo == "salida":
            if movimiento.producto.stock >= movimiento.cantidad:
                movimiento.producto.stock -=movimiento.cantidad
            else:
                form.add_error("Cantidad", "No hay stock suficiente")
                return self.form_invalid(form)
        
        movimiento.producto.save()
        movimiento.save()

        messages.success(self.request, f"Movimiento de stock registrado exitosamente")
        return redirect("productos:producto_detail", pk=movimiento.producto.pk)

class AjusteStockView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = AjusteStockForm
    template_name = "productos/ajuste_stock_form.html"
    login_url = 'account_login'

    permission_required = (
        "productos.change_producto",
        "productos.add_movimientostock",
    )

    def has_permission(self):
        user = self.request.user

        if not super().has_permission():
            return False

        if user.is_superuser:
            return True
                
        return (super().has_permission() and self.request.user.groups.filter(name__in=["stock", "administradores"]).exists())

    def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            kwargs["producto"] = get_object_or_404(Producto, pk=self.kwargs["pk"])
            return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["producto"] = get_object_or_404(Producto, pk=self.kwargs["pk"])

    def form_valid(self, form):
        producto = get_object_or_404(Producto, pk= self.kwargs["pk"])
        nueva_cantidad = form.clened_data["cantidad"]
        motivo = form.cleaned_data["motivo"] or "Ajuste de stock"

        diferencia = nueva_cantidad - producto.stock

        if diferencia != 0:
            tipo = "entrada" if diferencia > 0 else "salida"
            MovimientoStock.objects.create(
                producto=producto, 
                tipo=tipo,
                cantidad=abs(diferencia),
                motivo=motivo,
                fecha=timezone.now(),
                usuario = self.request.user.username
            )

            producto.stock = nueva_cantidad
            producto.save()

            messages.success(self.request, f"Stock actualizado exitosamente")
        else:
            messages.info(self.request, f"El stock no ha cambiado")

        return redirect("productos:producto_detail", pk=producto.pk)


class StockBajoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Producto
    template_name = "productos/stock_bajo_list.html"
    context_object_name = "productos"
    login_url = 'account_login'
    paginate_by = 5

    permission_required = "productos.view_producto"

    def has_permission(self):
        user = self.request.user

        if not super().has_permission():
            return False

        if user.is_superuser:
            return True
                
        return (super().has_permission() and self.request.user.groups.filter(name__in=["stock", "administradores"]).exists())

    def get_queryset(self):
        return Producto.objects.filter(stock__lt=F("stock_minimo")).order_by("stock")
    

class MovimientoStockListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = MovimientoStock
    template_name = "productos/movimiento_list.html"
    context_object_name = "movimientos"
    login_url = 'account_login'
    paginate_by = 5

    permission_required = "productos.view_movimientostock"

    def has_permission(self):
        user = self.request.user

        if not super().has_permission():
            return False

        if user.is_superuser:
            return True
                
        return (super().has_permission() and self.request.user.groups.filter(name__in=["stock", "administradores"]).exists())
    
    def get_queryset(self):
        self.producto = get_object_or_404(Producto, pk=self.kwargs["pk"])
        return (
            MovimientoStock.objects
            .filter(producto=self.producto)
            .order_by("-fecha")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["producto"] = self.producto
        return context