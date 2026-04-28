from django.conf import settings
from django.db import models


class CSVUpload(models.Model):
    title = models.CharField(max_length=180)
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    file = models.FileField(upload_to='csv_uploads/')
    original_filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-year', '-month', '-uploaded_at']

    def __str__(self):
        return f'{self.title} ({self.month:02d}/{self.year})'

    def delete(self, *args, **kwargs):
        storage = self.file.storage if self.file else None
        name = self.file.name if self.file else None
        result = super().delete(*args, **kwargs)
        if storage and name and storage.exists(name):
            storage.delete(name)
        return result


class CSVRow(models.Model):
    upload = models.ForeignKey(CSVUpload, related_name='rows', on_delete=models.CASCADE)
    row_number = models.PositiveIntegerField()
    date_text = models.CharField(max_length=80, blank=True)
    unit = models.CharField(max_length=120, blank=True)
    payment_method = models.CharField(max_length=160, blank=True)
    concept = models.TextField(blank=True)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    comments = models.TextField(blank=True)
    raw_data = models.JSONField(default=dict)

    class Meta:
        ordering = ['upload_id', 'row_number']

    def __str__(self):
        return f'{self.upload_id} #{self.row_number} {self.unit} ${self.total}'
