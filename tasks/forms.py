from django import forms
from django.forms import ModelForm

from .models import Area, Finanza, Limpieza, Mantenimientos
from .catalogs import (
    AREA_STATUS_CHOICES,
    DEFAULT_AREA_NAMES,
    DEFAULT_AREA_SPECS,
    MAINTENANCE_RESPONSIBLE_CHOICES,
    MAINTENANCE_TOPIC_CHOICES,
)


AREA_TIPO_CHOICES = [
    ('', 'Selecciona...'),
    ('Oficina', 'Oficina'),
    ('Departamento', 'Departamento'),
    ('Lobby', 'Lobby'),
    ('Estacionamiento', 'Estacionamiento'),
    ('Bodega', 'Bodega'),
    ('Cuarto de maquinas', 'Cuarto de maquinas'),
    ('Pasillo', 'Pasillo'),
    ('Escaleras', 'Escaleras'),
    ('Roof top', 'Roof top'),
    ('Area comun', 'Area comun'),
]

AREA_ESTADO_CHOICES = [
    ('', 'Selecciona...'),
    *AREA_STATUS_CHOICES,
]

MANTENIMIENTO_TITULO_CHOICES = [
    ('', 'Selecciona tema...'),
    *MAINTENANCE_TOPIC_CHOICES,
]

MANTENIMIENTO_ESTADO_CHOICES = [
    ('Pendiente', 'Pendiente'),
    ('En progreso', 'En Progreso'),
    ('Detenido', 'Detenido'),
    ('Completado', 'Completado'),
    ('Cancelado', 'Cancelado'),
]

PRIORIDAD_CHOICES = [
    ('Baja', 'Baja'),
    ('Media', 'Media'),
    ('Alta', 'Alta'),
    ('Critica', 'Critica'),
]

CLAVE_INMUEBLE_CHOICES = [
    ('', 'Selecciona una clave'),
    ('boss8025', 'boss8025'),
    ('C1438', 'C1438'),
]

FINANZA_STATUS_CHOICES = [
    ('', 'Selecciona un estado'),
    ('Pendiente', 'Pendiente'),
    ('Pagado', 'Pagado'),
]


class AreaForm(forms.ModelForm):
    nombre = forms.ChoiceField(choices=[], required=True)
    tipo_area = forms.ChoiceField(choices=AREA_TIPO_CHOICES, required=False)
    estado = forms.ChoiceField(choices=AREA_ESTADO_CHOICES, required=False)

    class Meta:
        model = Area
        fields = ['nombre', 'numero_piso', 'tipo_area', 'estado', 'ubicacion']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_name = self.instance.nombre if self.instance and self.instance.pk else None
        existing_names = set()
        if not current_name:
            existing_names = set(Area.objects.filter(nombre__in=DEFAULT_AREA_NAMES).values_list('nombre', flat=True))
        choices = [(name, name) for name in DEFAULT_AREA_NAMES if name == current_name or name not in existing_names]
        if current_name and current_name not in DEFAULT_AREA_NAMES:
            choices.insert(0, (current_name, current_name))
        self.fields['nombre'].choices = [('', 'Selecciona un area fija...'), *choices]
        self.fields['numero_piso'].widget.attrs['readonly'] = True
        self.fields['tipo_area'].widget.attrs['disabled'] = True
        self.fields['ubicacion'].widget.attrs['readonly'] = True

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if nombre not in DEFAULT_AREA_NAMES:
            raise forms.ValidationError('Selecciona un area del catalogo fijo.')
        existing = Area.objects.filter(nombre=nombre)
        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError('Esta area fija ya existe. Edita su registro actual.')
        return nombre

    def clean(self):
        cleaned_data = super().clean()
        area_specs = {name: (floor, kind) for name, floor, kind in DEFAULT_AREA_SPECS}
        nombre = cleaned_data.get('nombre')
        if nombre in area_specs:
            floor, kind = area_specs[nombre]
            cleaned_data['numero_piso'] = floor
            cleaned_data['tipo_area'] = kind
            cleaned_data['ubicacion'] = 'BOSS8025'
        return cleaned_data


class MantenimientoForm(ModelForm):
    titulo = forms.ChoiceField(choices=MANTENIMIENTO_TITULO_CHOICES)
    responsable = forms.ChoiceField(choices=[('', 'Selecciona...'), *MAINTENANCE_RESPONSIBLE_CHOICES])
    estado = forms.ChoiceField(choices=MANTENIMIENTO_ESTADO_CHOICES, initial='Pendiente')
    prioridad = forms.ChoiceField(choices=PRIORIDAD_CHOICES, initial='Media')

    class Meta:
        model = Mantenimientos
        fields = ['titulo', 'descripcion', 'fecha_inicio', 'fecha_final', 'archivo', 'responsable', 'ubicacion', 'estado', 'prioridad']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_final': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ubicacion'].label = 'Area'
        self.fields['ubicacion'].empty_label = 'Selecciona un area...'
        self.fields['ubicacion'].queryset = Area.objects.order_by('nombre')

        if self.instance and self.instance.pk:
            current_title = self.instance.titulo
            known_titles = {value for value, _ in MANTENIMIENTO_TITULO_CHOICES}
            if current_title and current_title not in known_titles:
                self.fields['titulo'].choices = [(current_title, current_title), *MANTENIMIENTO_TITULO_CHOICES]

            current_responsable = self.instance.responsable
            known_responsables = {value for value, _ in self.fields['responsable'].choices}
            if current_responsable and current_responsable not in known_responsables:
                self.fields['responsable'].choices = [(current_responsable, current_responsable), *self.fields['responsable'].choices]


class LimpiezaForm(ModelForm):
    class Meta:
        model = Limpieza
        fields = ['titulo', 'descripcion', 'responsable', 'area', 'fecha_programada', 'estado']
        widgets = {
            'fecha_programada': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class FinanzaForm(ModelForm):
    clave_inmueble = forms.ChoiceField(choices=CLAVE_INMUEBLE_CHOICES)
    status = forms.ChoiceField(choices=FINANZA_STATUS_CHOICES, required=False)
    departamento = forms.ChoiceField(choices=[], required=False)

    class Meta:
        model = Finanza
        fields = [
            'clave_inmueble',
            'departamento',
            'mes',
            'anio',
            'tipo_movimiento',
            'categoria',
            'concepto',
            'costo',
            'fecha_pago',
            'gas',
            'fecha_pago_gas',
            'agua',
            'fecha_pago_agua',
            'luz',
            'fecha_pago_luz',
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
        widgets = {
            'anio': forms.NumberInput(attrs={'min': 2000, 'max': 2100}),
            'fecha_pago': forms.DateInput(attrs={'type': 'date'}),
            'fecha_pago_gas': forms.DateInput(attrs={'type': 'date'}),
            'fecha_pago_agua': forms.DateInput(attrs={'type': 'date'}),
            'fecha_pago_luz': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_movimiento = cleaned_data.get('tipo_movimiento')
        categoria = cleaned_data.get('categoria')

        if categoria == 'Renta':
            cleaned_data['tipo_movimiento'] = 'Ingreso'
        elif tipo_movimiento == 'Ingreso' and categoria != 'Renta':
            raise forms.ValidationError('Los ingresos deben registrarse con la categoria Renta.')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        area_choices = [(area.nombre, area.nombre) for area in Area.objects.order_by('numero_piso', 'nombre')]
        current_departamento = self.instance.departamento if self.instance and self.instance.pk else None
        if current_departamento and current_departamento not in {value for value, _ in area_choices}:
            area_choices.insert(0, (current_departamento, current_departamento))
        self.fields['departamento'].choices = [('', 'Selecciona un area/departamento...'), *area_choices]
        self.fields['departamento'].label = 'Area o departamento'


class RestoreForm(forms.Form):
    backup_file = forms.FileField(label='Archivo de Respaldo')
