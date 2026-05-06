from django import forms

from .models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['area', 'task', 'frequency', 'css_class']
        labels = {
            'area': 'Area',
            'task': 'Etiqueta / actividad',
            'frequency': 'Periodicidad',
            'css_class': 'Estilo',
        }
