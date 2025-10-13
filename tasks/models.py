from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Area(models.Model):
    nombre = models.CharField(max_length=100, unique=True)  # Ej: "Departamento 101"
    numero_piso = models.PositiveIntegerField(null=True, blank=True)  # Permite null al agregar el campo
    tipo_area = models.CharField(max_length=50, null=True, blank=True)  # Ej: "Departamento", "Oficina", etc.
    estado = models.CharField(max_length=20, null=True, blank=True)  # Ej: "Libre", "Ocupado", "Mantenimiento"
    ubicacion = models.CharField(max_length=100, blank=True, null=True)  # Ej: "Torre A, ala norte"
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Permite null hasta que asignes usuarios

    def __str__(self):
        return self.nombre

class Mantenimientos(models.Model):
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    responsable = models.CharField(max_length=100)
    
    ubicacion = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True, db_constraint=False)

    archivo = models.FileField(upload_to='uploads/', blank=True, null=True)

    estado = models.CharField(max_length=50, blank=True)  # Ej: "Completado "
    prioridad = models.CharField(max_length=50, blank=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.estado == "Completado" and self.fecha_completado is None:
            self.fecha_completado = timezone.now()
        elif self.estado != "Completado ":
            self.fecha_completado = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titulo} - by {self.user.username}"


class Limpieza(models.Model):   
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En progreso', 'En progreso'),
        ('Completado', 'Completado'),
    ]
    
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    responsable = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    fecha_programada = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Finanza(models.Model):
    titulo = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10)
    categoria = models.CharField(max_length=50, blank=True, null=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.titulo} - {self.tipo} - ${self.monto}"
    

class EntradaAlrededores(models.Model):
    nombre = models.CharField(max_length=200)          # PISO, TAPETE DE ENTRADA, etc.
    periodicidad = models.CharField(max_length=100)    # DIARIO, MARTES Y VIERNES, etc.
    orden = models.PositiveIntegerField(default=0)     # para ordenar en la tabla
    activo = models.BooleanField(default=True)
    fecha = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nombre