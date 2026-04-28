from django.forms import ModelForm
from .models import Mantenimientos, Limpieza, Finanza, Area
from django import forms
from django.contrib.auth import get_user_model

AREA_TIPO_CHOICES = [
    ('', 'Selecciona...'),
    ('Oficina', 'Oficina'),
    ('Departamento', 'Departamento'),
    ('Sala de Reuniones', 'Sala de Reuniones'),
    ('Area Comun', 'Area Comun'),
]

AREA_ESTADO_CHOICES = [
    ('', 'Selecciona...'),
    ('Libre', 'Libre'),
    ('Ocupado', 'Ocupado'),
    ('Mantenimiento', 'Mantenimiento'),
]

MANTENIMIENTO_TITULO_CHOICES = [
    ('', 'Selecciona tipo...'),
    ('Aguakan', 'Aguakan'),
    ('alberca', 'Alberca'),
    ('asador en roof', 'Asador en Roof'),
    ('camaras', 'CÃ¡maras'),
    ('CFE', 'CFE'),
    ('cuarto de bombas', 'Cuarto de Bombas'),
    ('elevador', 'Elevador'),
    ('espacio holistico', 'Espacio HolÃ­stico'),
    ('estacionamiento', 'Estacionamiento'),
    ('fumigaciÃ³n', 'FumigaciÃ³n'),
    ('gas', 'Gas'),
    ('gym', 'Gym'),
    ('hidraÃºlico', 'HidrÃ¡ulico'),
    ('internet', 'Internet'),
    ('limpieza', 'Limpieza'),
    ('lobby', 'Lobby'),
    ('oficina', 'Oficina'),
    ('porton automÃ¡tico', 'PortÃ³n AutomÃ¡tico'),
    ('sala en roof', 'Sala en Roof'),
    ('Seguimiento mantenimiento', 'Seguimiento mantenimiento'),
    ('otro', 'Otro...'),
]

MANTENIMIENTO_ESTADO_CHOICES = [
    ('Pendiente', 'Pendiente'),
    ('En progreso', 'En Progreso'),
    ('Completado', 'Completado'),
    ('Cancelado', 'Cancelado'),
]

PRIORIDAD_CHOICES = [
    ('Baja', 'Baja'),
    ('Media', 'Media'),
    ('Alta', 'Alta'),
    ('CrÃ­tica', 'CrÃ­tica'),
]

CLAVE_INMUEBLE_CHOICES = [
    ('', 'Selecciona una clave'),
    ('boss8025', 'boss8025'),
    ('C1438', 'C1438'),
]

FINANZA_STATUS_CHOICES = [
    ('', 'Selecciona un estado'),
    ('Pendiente', 'Pendiente'),
    ('Completado', 'Completado'),
]

class AreaForm(forms.ModelForm):
    tipo_area = forms.ChoiceField(choices=AREA_TIPO_CHOICES, required=False)
    estado = forms.ChoiceField(choices=AREA_ESTADO_CHOICES, required=False)

    class Meta:
        model = Area
        fields = ['nombre', 'numero_piso', 'tipo_area', 'estado', 'ubicacion'] 

class MantenimientoForm(ModelForm):
    titulo = forms.ChoiceField(choices=MANTENIMIENTO_TITULO_CHOICES)
    titulo_otro = forms.CharField(required=False, max_length=100)
    responsable = forms.ChoiceField(choices=[])
    estado = forms.ChoiceField(choices=MANTENIMIENTO_ESTADO_CHOICES, initial='Pendiente')
    prioridad = forms.ChoiceField(choices=PRIORIDAD_CHOICES, initial='Media')

    class Meta:
        model = Mantenimientos
        fields = ['titulo', 'descripcion','archivo', 'responsable', 'ubicacion', 'estado', 'prioridad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        User = get_user_model()
        user_choices = [
            (user.username, user.get_full_name() or user.username)
            for user in User.objects.order_by('username')
        ]
        self.fields['responsable'].choices = [('', 'Selecciona...'), *user_choices]
        self.fields['ubicacion'].label = 'Area'
        self.fields['ubicacion'].empty_label = 'Selecciona un area...'
        self.fields['ubicacion'].queryset = Area.objects.order_by('nombre')

        if self.instance and self.instance.pk:
            current_title = self.instance.titulo
            known_titles = {value for value, _ in MANTENIMIENTO_TITULO_CHOICES}
            if current_title and current_title not in known_titles:
                self.fields['titulo'].choices = [
                    (current_title, current_title),
                    *MANTENIMIENTO_TITULO_CHOICES,
                ]
            current_responsable = self.instance.responsable
            known_responsables = {value for value, _ in self.fields['responsable'].choices}
            if current_responsable and current_responsable not in known_responsables:
                self.fields['responsable'].choices = [
                    (current_responsable, current_responsable),
                    *self.fields['responsable'].choices,
                ]

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        titulo_otro = self.cleaned_data.get('titulo_otro', '').strip()
        if titulo == 'otro':
            if not titulo_otro:
                raise forms.ValidationError('Especifica el tÃ­tulo.')
            return titulo_otro
        return titulo

class LimpiezaForm(ModelForm):
    class Meta:
        model = Limpieza
        fields = ['titulo', 'descripcion', 'responsable', 'area', 'fecha_programada', 'estado']
class FinanzaForm(ModelForm):
    clave_inmueble = forms.ChoiceField(choices=CLAVE_INMUEBLE_CHOICES)
    status = forms.ChoiceField(choices=FINANZA_STATUS_CHOICES, required=False)

    class Meta:
        model = Finanza
        fields = [
            'clave_inmueble',
            'concepto',
            'costo',
            'solicita',
            'autoriza',
            'status',
            'proveedor',
            'factura',
            'observaciones',
            'cta_bancaria',
            'clabe',
            'banco',
            'nombre',
            'rfc',
        ]


class RestoreForm(forms.Form):
    backup_file = forms.FileField(label='Archivo de Respaldo')
