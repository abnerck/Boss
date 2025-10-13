from django.forms import ModelForm
from .models import Mantenimientos, Limpieza, Finanza, Area
from django import forms

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['nombre', 'numero_piso', 'tipo_area', 'estado', 'ubicacion'] 

class MantenimientoForm(ModelForm):
    class Meta:
        model = Mantenimientos
        fields = ['titulo', 'descripcion','archivo', 'responsable', 'ubicacion', 'estado', 'prioridad']

class LimpiezaForm(ModelForm):
    class Meta:
        model = Limpieza
        fields = ['titulo', 'descripcion', 'responsable', 'area', 'fecha_programada', 'estado']

class FinanzaForm(ModelForm):
    class Meta:
        model = Finanza
        fields = ['titulo', 'tipo', 'categoria', 'monto','descripcion']


class RestoreForm(forms.Form):
    backup_file = forms.FileField(label='Archivo de Respaldo')