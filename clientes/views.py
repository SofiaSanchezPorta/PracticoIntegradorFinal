from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q, F
from django.utils import timezone
from .models import Cliente
from .forms import ClienteForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models.deletion import ProtectedError


class ClienteListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Cliente
    template_name = "clientes/cliente_list.html"
    context_object_name = "clientes"
    login_url = 'account_login'
    paginate_by = 5

    permission_required = "clientes.view_cliente"

    def has_permission(self):
        user = self.request.user

        if not super().has_permission():
            return False

        if user.is_superuser:
            return True
                
        return (super().has_permission() and self.request.user.groups.filter(name__in=["ventas", "administradores"]).exists())


class ClienteDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Cliente
    template_name = "clientes/cliente_detail.html"
    context_object_name = "cliente"
    login_url = 'account_login'

    permission_required = "clientes.view_cliente"

    def has_permission(self):
        user = self.request.user

        if not super().has_permission():
            return False

        if user.is_superuser:
            return True
        
        return (super().has_permission() and self.request.user.groups.filter(name__in=["ventas", "administradores"]).exists())


class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/cliente_form.html"
    success_url = reverse_lazy("clientes:cliente_list")
    login_url = 'account_login'

    permission_required = "clientes.add_cliente"

    def has_permission(self):
        user = self.request.user

        if not super().has_permission():
            return False

        if user.is_superuser:
            return True
        
        return (super().has_permission() and self.request.user.groups.filter(name__in=["ventas", "administradores"]).exists())


class ClienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/cliente_form.html"
    success_url = reverse_lazy("clientes:cliente_list")
    login_url = 'account_login'

    permission_required = "clientes.change_cliente"

    def has_permission(self):
        user = self.request.user

        if not super().has_permission():
            return False

        if user.is_superuser:
            return True
        
        return (super().has_permission() and self.request.user.groups.filter(name__in=["ventas", "administradores"]).exists())

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Cliente actualizado exitosamente")
        return response

class ClienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Cliente
    template_name = "clientes/cliente_delete.html"
    context_object_name = "cliente"
    success_url = reverse_lazy("clientes:cliente_list")
    login_url = "account_login"

    permission_required = ("clientes.delete_cliente",)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar el cliente porque tiene ventas asociadas."
            )
            return redirect("clientes:cliente_detail", pk=self.object.pk)
        
"""
class ClienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Cliente
    template_name = "clientes/cliente_delete.html"
    context_object_name = "cliente"
    success_url = reverse_lazy("clientes:cliente_list")
    login_url = 'account_login'

    permission_required = "clientes.delete_cliente"

    def has_permission(self):
        user = self.request.user

        if not super().has_permission():
            return False

        if user.is_superuser:
            return True
                
        return (super().has_permission() and self.request.user.groups.filter(name__in=["ventas", "administradores"]).exists())

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, "Cliente eliminado correctamente.")
            return HttpResponseRedirect(self.get_success_url())
        except ProtectedError:
            messages.error(
                request,
                "No se puede eliminar el cliente porque tiene ventas asociadas."
            )
            return redirect("clientes:cliente_detail", pk=self.object.pk)
            """