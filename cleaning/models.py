from django.db import models
from django.contrib.auth.models import User
from datetime import date  # Para default si lo usas

class Activity(models.Model):
    area = models.CharField(max_length=100)
    task = models.CharField(max_length=200)
    frequency = models.CharField(max_length=100)
    css_class = models.CharField(max_length=20, default='')

    def __str__(self):
        return f"{self.task} - {self.frequency}"

    class Meta:
        ordering = ['area', 'id']
        verbose_name = 'Actividad'  # Opcional: para admin en español
        verbose_name_plural = 'Actividades'

class CleaningLog(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    date = models.DateField()  # Sin auto_now_add; set manual en views
    completed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)  # Mantiene esto para hora de creación

    def __str__(self):
        return f"{self.activity.task} - {self.date} - {'Completado' if self.completed else 'Pendiente'}"

    class Meta:
        ordering = ['-date', '-timestamp']
        unique_together = ['activity', 'date', 'user']  # Previene duplicados
        indexes = [models.Index(fields=['date', 'user'])]  # Para queries rápidas en history
        verbose_name = 'Log de Limpieza'
        verbose_name_plural = 'Logs de Limpieza'