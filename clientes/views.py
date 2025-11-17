from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q, F
from django.utils import timezone
from .models import Cliente
from .forms import ClienteForm
#from .forms import ProductoForm, MovimientoStockForm, AjusteStockForm

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


class ClienteListView(ListView):
    model = Cliente
    template_name = "clientes/cliente_list.html"
    context_object_name = "clientes"


class ClienteDetailView(DetailView):
    model = Cliente
    template_name = "clientes/cliente_detail.html"
    context_object_name = "cliente"


class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/cliente_form.html"
    success_url = reverse_lazy("clientes:cliente_list")


class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = "clientes/cliente_form.html"
    success_url = reverse_lazy("clientes:cliente_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Cliente actualizado exitosamente")
        return response

class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = "clientes/cliente_delete.html"
    context_object_name = "cliente"
    success_url = reverse_lazy("clientes:cliente_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Cliente eliminado exitosamente")
        return super().delete(request, *args, **kwargs)