from django.contrib import admin

from .models import CSVRow, CSVUpload


@admin.register(CSVUpload)
class CSVUploadAdmin(admin.ModelAdmin):
    list_display = ('title', 'month', 'year', 'original_filename', 'uploaded_by', 'uploaded_at')
    list_filter = ('year', 'month')
    search_fields = ('title', 'original_filename')


@admin.register(CSVRow)
class CSVRowAdmin(admin.ModelAdmin):
    list_display = ('upload', 'row_number', 'unit', 'payment_method', 'total')
    list_filter = ('upload__year', 'upload__month', 'payment_method')
    search_fields = ('unit', 'concept', 'comments')
