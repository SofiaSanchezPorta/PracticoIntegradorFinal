from django.db import models
import os
import uuid
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

class Cliente(models.Model):
    """Model definition for Cliente."""

    nombre = models.CharField("Nombre", max_length=50)
    apellido = models.CharField("Apellido", max_length=50)
    #PARA EL DNI PONEMOS UN NÚMERO DESDE UN MILLÓN A 60 MILLONES
    dni = models.PositiveIntegerField("DNI", validators=[
        MinValueValidator(1000000),
        MaxValueValidator(60000000)
    ], unique=True)
    #PARA EL TELÉFONO PONEMOS UN NÚMERO DE 13 DÍGIDOS
    telefono = models.PositiveIntegerField("Teléfono", validators=[
        MinValueValidator(0000000000000),
        MaxValueValidator(9999999999999)
    ])
    mail = models.EmailField("Email", max_length=254)

    class Meta:
        """Meta definition for Cliente."""

        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['apellido'] #ORDENA POR NOMBRE AUTOMÁTICAMENTE

    def __str__(self):
        """Unicode representation of Cliente."""
        return f"{self.nombre} {self.apellido}"

