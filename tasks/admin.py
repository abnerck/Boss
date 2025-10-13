from django.contrib import admin
from .models import Mantenimientos

class MantenimientoAdmin(admin.ModelAdmin):
    readonly_fields = ("fecha_creacion",)

admin.site.register(Mantenimientos, MantenimientoAdmin)
