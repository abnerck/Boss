from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, date, timedelta
from collections import defaultdict
import json
from .models import Activity, CleaningLog

# Lista COMPLETA de actividades
activities = [
    {'area': 'Área de Entrada y Alrededores', 'task': 'PISO', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Área de Entrada y Alrededores', 'task': 'TAPETE DE ENTRADA', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Área de Entrada y Alrededores', 'task': 'AREA DE BASURA', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Área de Entrada y Alrededores', 'task': 'VENTANALES', 'frequency': 'MARTES', 'css_class': ''},
    {'area': 'Área de Entrada y Alrededores', 'task': 'MACETAS Y RIEGO', 'frequency': 'MARTES Y VIERNES', 'css_class': ''},
    {'area': 'Área de Entrada y Alrededores', 'task': 'BOTES DE BASURA', 'frequency': 'LUNES Y MIERCOLES', 'css_class': ''},
    {'area': 'Lobby', 'task': 'PISO', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Lobby', 'task': 'MESA', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Lobby', 'task': 'ADORNO DE MESA', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Lobby', 'task': 'SILLONES', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Lobby', 'task': 'PUERTA', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Lobby', 'task': 'LAMPARA DE CRISTAL', 'frequency': 'LUNES', 'css_class': ''},
    {'area': 'Lobby', 'task': 'VENTANALES', 'frequency': 'MARTES', 'css_class': ''},
    {'area': 'Lobby', 'task': 'MACETA (SIN HOJAS SECAS Y REGADAS)', 'frequency': 'MARTES Y VIERNES', 'css_class': ''},
    {'area': 'Lobby', 'task': 'ESPEJO', 'frequency': 'MIÉRCOLES', 'css_class': ''},
    {'area': 'Lobby', 'task': 'PAREDES', 'frequency': 'QUINCENAL JUEVES', 'css_class': 'biweekly'},
    {'area': 'Lobby', 'task': 'HERRERIA', 'frequency': 'SÁBADO', 'css_class': ''},
    {'area': 'Escaleras', 'task': 'DEL LOBBY AL 1º PISO', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Escaleras', 'task': 'DEL 1º PISO AL 2º PISO', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Escaleras', 'task': 'DEL 2º PISO AL 3º PISO', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Escaleras', 'task': 'DEL 3º PISO A LA AZOTEA', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Escaleras', 'task': 'LIMPIEZA PROFUNDA DEL 1º PISO AL 2º PISO', 'frequency': 'QUINCENAL LUNES', 'css_class': 'biweekly'},
    {'area': 'Escaleras', 'task': 'LIMPIEZA PROFUNDA DEL 2º PISO AL 3º PISO', 'frequency': 'QUINCENAL MIERCOLES', 'css_class': 'biweekly'},
    {'area': 'Escaleras', 'task': 'LIMPIEZA PROFUNDA DEL 3º PISO A LA AZOTEA', 'frequency': 'QUINCENAL VIERNES', 'css_class': 'biweekly'},
    {'area': 'Escaleras', 'task': 'LIMPIEZA PROFUNDA DEL LOBBY AL 1º PISO', 'frequency': 'SÁBADO', 'css_class': ''},
    {'area': 'Elevador', 'task': 'CAJA DEL ELEVADOR (PAREDES, PISO Y CONTROLES)', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Elevador', 'task': 'EXTERIOR ELEVADOR LOBBY', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Elevador', 'task': 'EXTERIOR ELEVADOR 1º PISO', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Elevador', 'task': 'EXTERIOR ELEVADOR 2º PISO', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Elevador', 'task': 'EXTERIOR ELEVADOR 3º PISO', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': '1º Piso', 'task': 'PISOS', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': '1º Piso', 'task': 'PAREDES', 'frequency': 'LUNES', 'css_class': ''},
    {'area': '1º Piso', 'task': 'CRISTALES Y BARANDAL DE CRISTAL', 'frequency': 'JUEVES', 'css_class': ''},
    {'area': '1º Piso', 'task': 'LAMPARAS Y FOCOS', 'frequency': 'JUEVES', 'css_class': ''},
    {'area': '1º Piso', 'task': 'HERRERIA: PUERTAS Y REJAS', 'frequency': 'SÁBADO', 'css_class': ''},
    {'area': '1º Piso', 'task': 'TECHOS', 'frequency': 'VIERNES', 'css_class': ''},
    {'area': '2º Piso', 'task': 'PISOS', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': '2º Piso', 'task': 'PAREDES', 'frequency': 'LUNES', 'css_class': ''},
    {'area': '2º Piso', 'task': 'CRISTALES Y BARANDAL DE CRISTAL', 'frequency': 'JUEVES', 'css_class': ''},
    {'area': '2º Piso', 'task': 'LAMPARAS Y FOCOS', 'frequency': 'JUEVES', 'css_class': ''},
    {'area': '2º Piso', 'task': 'HERRERIA: PUERTAS Y REJAS', 'frequency': 'SÁBADO', 'css_class': ''},
    {'area': '2º Piso', 'task': 'TECHOS', 'frequency': 'VIERNES', 'css_class': ''},
    {'area': '3º Piso', 'task': 'PISOS', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': '3º Piso', 'task': 'PAREDES', 'frequency': 'LUNES', 'css_class': ''},
    {'area': '3º Piso', 'task': 'CRISTALES Y BARANDAL DE CRISTAL', 'frequency': 'JUEVES', 'css_class': ''},
    {'area': '3º Piso', 'task': 'LAMPARAS Y FOCOS', 'frequency': 'JUEVES', 'css_class': ''},
    {'area': '3º Piso', 'task': 'HERRERIA: PUERTAS Y REJAS', 'frequency': 'SÁBADO', 'css_class': ''},
    {'area': '3º Piso', 'task': 'TECHOS', 'frequency': 'VIERNES', 'css_class': ''},
    {'area': 'Azotea (Roof)', 'task': 'REVISION DE NIVEL DE AGUA ALBERCA DEBE LLEGAR A LA CANASTILLA', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Azotea (Roof)', 'task': 'PISO', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Azotea (Roof)', 'task': 'SILLONES', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Azotea (Roof)', 'task': 'MESA', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Azotea (Roof)', 'task': 'CAMASTROS', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Azotea (Roof)', 'task': 'CESTOS DE BASURA', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Azotea (Roof)', 'task': 'PISO ALREDEDOR DE ALBERCA', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Azotea (Roof)', 'task': 'REGADERA', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Azotea (Roof)', 'task': 'COCINETA: BARRA, ENTREPAÑOS Y PISO', 'frequency': 'LUNES Y VIERNES', 'css_class': ''},
    {'area': 'Azotea (Roof)', 'task': 'PARRILLA', 'frequency': 'LUNES', 'css_class': ''},
    {'area': 'Azotea (Roof)', 'task': 'BARANDALES ALBERCA', 'frequency': 'VIERNES', 'css_class': ''},
    {'area': 'Azotea Baños', 'task': 'PISOS', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Azotea Baños', 'task': 'PAREDES', 'frequency': 'LUNES Y VIERNES', 'css_class': ''},
    {'area': 'Azotea Baños', 'task': 'TECHOS', 'frequency': 'QUINCENAL VIERNES', 'css_class': 'biweekly'},
    {'area': 'Azotea Baños', 'task': 'LAVAMANOS', 'frequency': 'LUNES - MIERCOLES - VIERNES', 'css_class': ''},
    {'area': 'Azotea Baños', 'task': 'EXCUSADOS Y TAPAS', 'frequency': 'LUNES - MIERCOLES - VIERNES', 'css_class': ''},
    {'area': 'Azotea Baños', 'task': 'CESTOS DE BASURA', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Azotea Baños', 'task': 'PUERTAS', 'frequency': 'LUNES Y JUEVES', 'css_class': ''},
    {'area': 'Gym', 'task': 'PISOS', 'frequency': 'QUINCENAL VIERNES', 'css_class': 'biweekly'},
    {'area': 'Gym', 'task': 'PAREDES', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Gym', 'task': 'TECHOS', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Gym', 'task': 'EQUIPOS DE EJERCICIOS', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Gym', 'task': 'VENTANALES', 'frequency': 'VIERNES', 'css_class': ''},
    {'area': 'Áreas Especiales', 'task': 'PATIO 1º PISO', 'frequency': 'LUNES - MIERCOLES - VIERNES', 'css_class': ''},
    {'area': 'Áreas Especiales', 'task': 'ESTACIONAMIENTO', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Áreas Especiales', 'task': 'ÁREA Y BODEGA DE LIMPIEZA', 'frequency': 'SÁBADO', 'css_class': ''},
    {'area': 'Áreas Especiales', 'task': 'ÁREA DE EQUIPOS A.A.', 'frequency': 'QUINCENAL VIERNES', 'css_class': 'biweekly'},
    {'area': 'Áreas Especiales', 'task': 'OFICINAS', 'frequency': 'LUNES - JUEVES', 'css_class': ''},
    {'area': 'Áreas Especiales', 'task': 'ÁREA CISTERNAS / TANQUE DE GAS', 'frequency': 'QUINCENAL VIERNES', 'css_class': 'biweekly'},
    {'area': 'Áreas Especiales', 'task': 'ÁREA Y BODEGA DE MANTENIMIENTO', 'frequency': 'QUINCENAL SÁBADO', 'css_class': 'biweekly'},
    {'area': 'Departamentos Desocupados', 'task': 'ABRIR REGADERA', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Departamentos Desocupados', 'task': 'JALAR AL EXCUSADO', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Departamentos Desocupados', 'task': 'ABRIR LLAVE DE LAVAMANOS 3 SEGUNDOS (BAÑO)', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Departamentos Desocupados', 'task': 'ABRIR LLAVE DE LAVAMANOS 3 SEGUNDOS (OTRO)', 'frequency': 'DIARIO', 'css_class': 'daily'},
    {'area': 'Departamentos Desocupados', 'task': 'PISOS', 'frequency': 'LUNES - JUEVES', 'css_class': ''},
    {'area': 'Departamentos Desocupados', 'task': 'MUEBLES CLOSETS', 'frequency': 'LUNES - JUEVES', 'css_class': ''},
    {'area': 'Departamentos Desocupados', 'task': 'VENTANALES', 'frequency': 'VIERNES', 'css_class': ''},
    {'area': 'Departamentos Desocupados', 'task': 'BAÑOS LIMPIEZA PROFUNDA', 'frequency': 'LUNES', 'css_class': ''},
    {'area': 'Departamentos Desocupados', 'task': 'COCINETA', 'frequency': 'LUNES', 'css_class': ''},
    {'area': 'Departamentos Desocupados', 'task': 'BALCONES', 'frequency': 'JUEVES', 'css_class': ''},
    {'area': 'Departamentos Desocupados', 'task': 'LAMPARAS Y VENTILADORES', 'frequency': 'QUINCENAL SÁBADO', 'css_class': 'biweekly'},
]

# Mapeo de días inglés a español
spanish_days = {
    'Monday': 'LUNES',
    'Tuesday': 'MARTES',
    'Wednesday': 'MIÉRCOLES',
    'Thursday': 'JUEVES',
    'Friday': 'VIERNES',
    'Saturday': 'SÁBADO',
    'Sunday': 'DOMINGO'
}

def matches_frequency(freq, day):
    if freq.upper() == 'DIARIO':
        return True
    freq_clean = freq.upper().replace(' Y ', ' ').replace(' - ', ' ')
    return day.upper() in freq_clean

def get_current_date():
    """Para pruebas: cambia a datetime.now() en producción"""
    return datetime.now()  # Fecha actual


@login_required 
def cleaning_schedule(request):
    # Poblar Activity si no existe (una vez, para migrar la lista a DB)
    if not Activity.objects.exists():
        for act in activities:
            Activity.objects.create(**act)
    
    current_date = get_current_date()
    current_day_en = current_date.strftime('%A')
    current_day = spanish_days.get(current_day_en, 'LUNES')
    today_str = current_date.strftime('%Y-%m-%d')
    today_date = current_date.date()
    
    # Filtra actividades para hoy
    filtered_activities = Activity.objects.filter(
        Q(frequency__exact='DIARIO') | Q(frequency__icontains=current_day)
    )
    
    # Agrupa por área
    grouped = defaultdict(list)
    for act in filtered_activities:
        grouped[act.area].append(act)
    
    # Orden fijo de áreas
    area_order = ['Área de Entrada y Alrededores', 'Lobby', 'Escaleras', 'Elevador', '1º Piso', '2º Piso',
                  '3º Piso', 'Azotea (Roof)', 'Azotea Baños', 'Gym', 'Áreas Especiales', 'Departamentos Desocupados']
    ordered_grouped = {area: grouped[area] for area in area_order if area in grouped}
    
    libres = 5  # Ejemplo; puedes calcularlo dinámicamente si quieres
    
    # Query logs para hoy (pre-marcar checkboxes)
    logs_dict = {}
    if request.user.is_authenticated:
        logs_today = CleaningLog.objects.filter(date=today_date, user=request.user).values('activity_id', 'completed')
        logs_dict = {int(log['activity_id']): log['completed'] for log in logs_today}
    
    # Lista de IDs completados
    completed_ids = [k for k, v in logs_dict.items() if v]
    
    context = {
        'grouped': ordered_grouped,
        'current_day': current_day,
        'today_str': today_str,
        'libres': libres,
        'total_activities': len(filtered_activities),
        'completed_ids': completed_ids
    }
    
    return render(request, 'cleaning/cleaning.html', context)

@csrf_exempt  # Temporal para depurar; revertir en producción
@login_required
def save_log(request):
    if request.method == 'POST':
        try:
            # Parsear JSON del cuerpo de la solicitud
            data = json.loads(request.body)
            activity_id = int(data.get('activity_id'))
            completed = data.get('completed') == True
            activity = get_object_or_404(Activity, id=activity_id)
            
            if not request.user.is_authenticated:
                return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=401)
            
            # Usa la fecha actual para consistencia
            log, created = CleaningLog.objects.update_or_create(
                activity=activity,
                date=date.today(),
                user=request.user,
                defaults={'completed': completed}
            )
            
            # Calcular estadísticas para la respuesta
            today = date.today()
            current_day = spanish_days.get(datetime.now().strftime('%A'), 'LUNES')
            total_activities = Activity.objects.filter(
                Q(frequency__exact='DIARIO') | Q(frequency__icontains=current_day)
            ).count()
            completed_count = CleaningLog.objects.filter(
                date=today, user=request.user, completed=True
            ).count()
            percentage = round((completed_count / total_activities * 100)) if total_activities > 0 else 0
            
            return JsonResponse({
                'success': True,
                'created': created,
                'completed': completed,
                'completed_count': completed_count,
                'total_count': total_activities,
                'percentage': percentage
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Cuerpo de la solicitud inválido'}, status=400)
        except (ValueError, Activity.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'ID de actividad inválido'}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required
def cleaning_reports(request):
    # Obtener la fecha seleccionada de los parámetros GET, por defecto hoy
    selected_date_str = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = date.today()
    
    today = date.today()
    yesterday = selected_date - timedelta(days=1)
    tomorrow = selected_date + timedelta(days=1)
    
    # Obtener día de la semana en español
    current_day_en = selected_date.strftime('%A')
    current_day = spanish_days.get(current_day_en, 'LUNES')
    
    # Actividades esperadas para el día seleccionado
    activities_for_day = Activity.objects.filter(
        Q(frequency__exact='DIARIO') | Q(frequency__icontains=current_day)
    )
    total_activities = activities_for_day.count()
    
    # Logs para el día seleccionado
    logs = CleaningLog.objects.filter(
        date=selected_date
    ).select_related('activity', 'user')
    
    # Actividades completadas
    completed_activities = logs.filter(completed=True)
    completed_count = completed_activities.count()
    
    # Actividades pendientes
    completed_activity_ids = completed_activities.values_list('activity_id', flat=True)
    pending_activities = activities_for_day.exclude(id__in=completed_activity_ids)
    
    # Estadísticas del día
    date_stats = {
        'completed': completed_count,
        'total': total_activities,
        'percentage': round((completed_count / total_activities * 100) if total_activities > 0 else 0),
        'pending': total_activities - completed_count
    }
    
    # Estadísticas por usuario
    user_stats = logs.values('user__username').annotate(
        completed=Count('id', filter=Q(completed=True)),
        total=Count('id')
    )
    
    # Estadísticas de los últimos 7 días
    last_7_days = []
    for i in range(6, -1, -1):
        day = selected_date - timedelta(days=i)
        day_activities = Activity.objects.filter(
            Q(frequency__exact='DIARIO') | Q(frequency__icontains=spanish_days.get(day.strftime('%A'), 'LUNES'))
        ).count()
        day_completed = CleaningLog.objects.filter(
            date=day, completed=True
        ).count()
        last_7_days.append({
            'date': day,
            'completed': day_completed,
            'total': day_activities,
            'percentage': round((day_completed / day_activities * 100) if day_activities > 0 else 0),
            'is_selected': day == selected_date
        })
    
    # Estadísticas semanales (desde el lunes de la semana del selected_date)
    start_of_week = selected_date - timedelta(days=selected_date.weekday())
    week_logs = CleaningLog.objects.filter(
        date__gte=start_of_week,
        date__lte=selected_date
    ).select_related('activity')
    week_stats = []
    for i in range((selected_date - start_of_week).days + 1):
        day = start_of_week + timedelta(days=i)
        day_activities = Activity.objects.filter(
            Q(frequency__exact='DIARIO') | Q(frequency__icontains=spanish_days.get(day.strftime('%A'), 'LUNES'))
        ).count()
        day_completed = CleaningLog.objects.filter(
            date=day, completed=True
        ).count()
        week_stats.append({
            'date': day,
            'completed': day_completed,
            'total': day_activities,
            'percentage': round((day_completed / day_activities * 100) if day_activities > 0 else 0)
        })
    
    # Logs agrupados por fecha (para compatibilidad con el template anterior)
    logs_all = CleaningLog.objects.filter(user=request.user).select_related('activity').order_by('-date')
    grouped_history = defaultdict(list)
    for log in logs_all:
        grouped_history[log.date.strftime('%Y-%m-%d')].append(log)
    
    context = {
        'grouped_history': dict(grouped_history),
        'total_logs': logs_all.count(),
        'selected_date': selected_date,
        'today': today,
        'yesterday': yesterday,
        'tomorrow': tomorrow,
        'date_stats': date_stats,
        'user_stats': user_stats,
        'completed_activities': completed_activities,
        'pending_activities': pending_activities,
        'last_7_days': last_7_days,
        'week_stats': week_stats,
        'start_of_week': start_of_week
    }
    return render(request, 'cleaning/cleaning_reports.html', context)