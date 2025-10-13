from django.contrib import admin
from .models import Activity, CleaningLog

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['area', 'task', 'frequency']
    list_filter = ['area', 'frequency']
    search_fields = ['task', 'area']

@admin.register(CleaningLog)
class CleaningLogAdmin(admin.ModelAdmin):
    list_display = ['activity', 'date', 'user', 'completed', 'timestamp']
    list_filter = ['date', 'completed', 'user']
    search_fields = ['activity__task', 'user__username']
    date_hierarchy = 'date'
    
    # Para ver porcentajes por día
    def changelist_view(self, request, extra_context=None):
        # Agregar estadísticas al contexto
        from django.db.models import Count, Q
        from datetime import date
        
        today = date.today()
        total_activities = Activity.objects.count()
        
        # Estadísticas de hoy
        today_completed = CleaningLog.objects.filter(date=today, completed=True).count()
        today_percentage = round((today_completed / total_activities * 100)) if total_activities > 0 else 0
        
        if extra_context is None:
            extra_context = {}
            
        extra_context['today_stats'] = {
            'completed': today_completed,
            'total': total_activities,
            'percentage': today_percentage
        }
        
        return super().changelist_view(request, extra_context=extra_context)