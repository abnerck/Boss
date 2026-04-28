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


class CSVUploadForm(forms.Form):
    title = forms.CharField(label='Nombre del reporte', max_length=180)
    month = forms.ChoiceField(label='Mes', choices=MONTH_CHOICES)
    year = forms.IntegerField(label='Año', min_value=2020, max_value=2100)
    file = forms.FileField(label='Archivo CSV')

    def clean_file(self):
        file = self.cleaned_data['file']
        if not file.name.lower().endswith('.csv'):
            raise forms.ValidationError('Sube un archivo con extension .csv.')
        return file


class CSVQuestionForm(forms.Form):
    question = forms.CharField(
        label='Pregunta para la IA',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'Ejemplo: ¿Cuánto se pagó por unidad este mes? ¿Qué unidades pagaron más?'
        }),
        max_length=1000,
    )
