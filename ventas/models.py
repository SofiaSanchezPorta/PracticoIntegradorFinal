from django.db import models
import os
import uuid
from django.core.exceptions import ValidationError
from clientes.models import Cliente
from productos.models import Producto

class Venta(models.Model):
    """Model definition for Venta."""

    codigo_venta = models.CharField( verbose_name="Código de venta", max_length=50)
    cliente = models.ForeignKey(Cliente, verbose_name="Cliente", on_delete=models.PROTECT, related_name='ventas',)
    fecha = models.DateTimeField(verbose_name="Fecha", auto_now_add=True)
    total = models.DecimalField(verbose_name="Total", max_digits=10, decimal_places=2, default=0)

    class Meta:
        """Meta definition for Venta."""

        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha']

    def __str__(self):
        """Unicode representation of Venta."""
        return f"Pedido #{self.codigo_venta} a nombre de {self.cliente.apellido}, {self.cliente.nombre} - Total: ${self.total} - fecha: {self.fecha.date()}"
    
    def calcula_total(self):
        self.total = sum(item.subtotal for item in self.items.all())
        self.save(update_fields=['total'])
    
class ItemVenta(models.Model):
    """Model definition for ItemVenta."""

    venta = models.ForeignKey(Venta, verbose_name="Venta", on_delete=models.CASCADE, related_name='items',)
    producto = models.ForeignKey(Producto, verbose_name="Producto", on_delete=models.PROTECT, related_name='items_venta')
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    precio_unitario = models.DecimalField(verbose_name="Precio unitario", max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(verbose_name="Subtotal", max_digits=10, decimal_places=2)

    class Meta:
        """Meta definition for ItemVenta."""

        verbose_name = 'ItemVenta'
        verbose_name_plural = 'ItemVentas'
        ordering = ['id']

    def __str__(self):
        """Unicode representation of ItemVenta."""
        return f"{self.producto.nombre} * {self.cantidad} - Subtotal = {self.subtotal} - (Nro de venta: {self.venta.codigo_venta})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.subtotal = self.cantidad * self.precio_unitario
        self.venta.calcular_total()  # Actualiza el total del pedido

    def clean(self):
        if self.cantidad > self.producto.stock:
            raise ValidationError(f"No hay stock suficiente de {self.producto.nombre}. Disponible: {self.producto.stock}")
