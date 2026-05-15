from django import forms


MONTH_CHOICES = [
    (1, 'Enero'),
    (2, 'Febrero'),
    (3, 'Marzo'),
    (4, 'Abril'),
    (5, 'Mayo'),
    (6, 'Junio'),
    (7, 'Julio'),
    (8, 'Agosto'),
    (9, 'Septiembre'),
    (10, 'Octubre'),
    (11, 'Noviembre'),
    (12, 'Diciembre'),
]


class MultipleCSVFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleCSVFileField(forms.FileField):
    widget = MultipleCSVFileInput

    def clean(self, data, initial=None):
        files = data if isinstance(data, (list, tuple)) else [data]
        cleaned_files = []
        for file in files:
            cleaned_files.append(super().clean(file, initial))
        return cleaned_files


class CSVUploadForm(forms.Form):
    title = forms.CharField(label='Nombre del reporte', max_length=180, required=False)
    month = forms.ChoiceField(label='Mes', choices=MONTH_CHOICES)
    year = forms.IntegerField(label='Año', min_value=2020, max_value=2100)
    file = MultipleCSVFileField(label='Archivos CSV')

    def clean_file(self):
        files = self.cleaned_data['file']
        for file in files:
            if not file.name.lower().endswith('.csv'):
                raise forms.ValidationError('Sube solo archivos con extension .csv.')
        return files


class CSVQuestionForm(forms.Form):
    question = forms.CharField(
        label='Pregunta para la IA',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Ejemplo: ¿Cuánto se pagó por unidad este mes? ¿Qué unidades pagaron más?'
        }),
        max_length=1000,
    )
