import calendar
import os
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordResetView
from django.db import IntegrityError
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from cleaning.models import Activity, CleaningLog
from cleaning.views import cleaning_reports, cleaning_schedule
from .catalogs import DEFAULT_AREA_NAMES, ensure_default_areas
from .forms import AreaForm, FinanzaForm, LimpiezaForm, MantenimientoForm, RestoreForm
from .models import Area, Finanza, Limpieza, Mantenimientos


def password_reset_view(request):
    return PasswordResetView.as_view()(request)


def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm()})

    email = request.POST.get('email', '').strip()
    if not email:
        return render(request, 'signup.html', {
            'form': UserCreationForm(),
            'error': 'El correo electronico es obligatorio',
        })

    if request.POST['password1'] != request.POST['password2']:
        return render(request, 'signup.html', {
            'form': UserCreationForm(),
            'error': 'Las contrasenas no coinciden',
        })

    try:
        user = User.objects.create_user(
            username=request.POST['username'],
            email=email,
            password=request.POST['password1'],
        )
        login(request, user)
        return redirect('mantenimientos')
    except IntegrityError:
        return render(request, 'signup.html', {
            'form': UserCreationForm(),
            'error': 'El usuario ya existe',
        })


def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {'form': AuthenticationForm})

    user = authenticate(
        request,
        username=request.POST['username'],
        password=request.POST['password'],
    )
    if user is None:
        return render(request, 'signin.html', {
            'form': AuthenticationForm,
            'error': 'Usuario o contrasena es incorrecta',
        })

    login(request, user)
    return redirect('mantenimientos')


@login_required
def mantenimientos(request):
    mantenimiento = Mantenimientos.objects.select_related('ubicacion', 'user').all().order_by('-fecha_creacion')
    return render(request, 'mantenimientos.html', {'mantenimiento': mantenimiento})


@login_required
def create_mantenimientos(request):
    if request.method == 'POST':
        form = MantenimientoForm(request.POST, request.FILES)
        if form.is_valid():
            mantenimiento = form.save(commit=False)
            mantenimiento.user = request.user
            mantenimiento.save()
            messages.success(request, 'Mantenimiento registrado con exito.')
            return redirect('mantenimientos')
        return render(request, 'create_mantenimientos.html', {
            'form': form,
            'error': f'Error en el formulario: {form.errors.as_text()}',
        })

    return render(request, 'create_mantenimientos.html', {'form': MantenimientoForm()})


@login_required
def mantenimientos_detail(request, mantenimiento_id):
    mantenimiento = get_object_or_404(Mantenimientos, pk=mantenimiento_id)
    form = MantenimientoForm(instance=mantenimiento)

    if request.method == 'POST':
        form = MantenimientoForm(request.POST, request.FILES, instance=mantenimiento)
        if form.is_valid():
            form.save()
            return redirect('mantenimientos')

    show_form = request.GET.get('edit') == 'true' or request.method == 'POST'
    return render(request, 'mantenimientos_detail.html', {
        'mantenimiento': mantenimiento,
        'form': form,
        'show_form': show_form,
    })


@login_required
def delete_mantenimientos(request, mantenimiento_id):
    if request.method != 'POST':
        return redirect('mantenimientos')

    if request.user.is_superuser:
        mantenimiento = get_object_or_404(Mantenimientos, pk=mantenimiento_id)
    else:
        mantenimiento = get_object_or_404(Mantenimientos, pk=mantenimiento_id, user=request.user)
    mantenimiento.delete()
    return redirect('mantenimientos')


@login_required
def limpiezas(request):
    limpiezas_list = Limpieza.objects.all().order_by('-fecha_programada')
    return render(request, 'limpiezas.html', {'limpiezas': limpiezas_list})


@login_required
def create_limpiezas(request):
    if request.method == 'POST':
        form = LimpiezaForm(request.POST)
        if form.is_valid():
            limpieza = form.save(commit=False)
            limpieza.user = request.user
            limpieza.save()
            return redirect('limpiezas')
        return render(request, 'create_limpieza.html', {
            'form': form,
            'error': 'Por favor provee un dato valido',
        })

    return render(request, 'create_limpieza.html', {'form': LimpiezaForm()})


@login_required
def limpiezas_detail(request, limpieza_id):
    limpieza = get_object_or_404(Limpieza, pk=limpieza_id)
    form = LimpiezaForm(instance=limpieza)

    if request.method == 'POST':
        form = LimpiezaForm(request.POST, instance=limpieza)
        if form.is_valid():
            form.save()
            return redirect('limpiezas')

    show_form = request.GET.get('edit') == 'true' or request.method == 'POST'
    return render(request, 'limpiezas_detail.html', {
        'limpieza': limpieza,
        'form': form,
        'show_form': show_form,
    })


@login_required
def delete_limpieza(request, limpieza_id):
    if request.method != 'POST':
        return redirect('limpiezas')

    if request.user.is_superuser:
        limpieza = get_object_or_404(Limpieza, pk=limpieza_id)
    else:
        limpieza = get_object_or_404(Limpieza, pk=limpieza_id, user=request.user)
    limpieza.delete()
    return redirect('limpiezas')


@login_required
def usuarios(request):
    return render(request, 'usuarios.html', {'usuarios': User.objects.all()})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('usuarios')
    else:
        form = UserCreationForm()
    return render(request, 'create_usuario.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if request.method == 'POST' and not usuario.is_superuser:
        usuario.delete()
    return redirect('usuarios')


@login_required
def finanzas(request):
    selected_year = request.GET.get('anio')
    selected_month = request.GET.get('mes')
    finanza_base = Finanza.objects.select_related('user').all()
    finanza = finanza_base.order_by('-fecha', '-id')

    if selected_year:
        finanza = finanza.filter(anio=selected_year)
    if selected_month:
        finanza = finanza.filter(mes=selected_month)

    ingresos = finanza.filter(tipo_movimiento='Ingreso').aggregate(total=Sum('total'))['total'] or 0
    egresos = finanza.filter(tipo_movimiento='Egreso').aggregate(total=Sum('total'))['total'] or 0
    balance = ingresos - egresos
    por_categoria = finanza.values('tipo_movimiento', 'categoria').annotate(total=Sum('total')).order_by('tipo_movimiento', 'categoria')
    por_periodo = (
        finanza_base.exclude(mes__isnull=True).exclude(anio__isnull=True)
        .values('anio', 'mes', 'tipo_movimiento')
        .annotate(total=Sum('total'))
        .order_by('-anio', '-mes', 'tipo_movimiento')[:24]
    )
    comparativo = []
    periodos = (
        finanza_base.exclude(mes__isnull=True).exclude(anio__isnull=True)
        .values('anio', 'mes')
        .annotate(
            ingresos=Sum('total', filter=Q(tipo_movimiento='Ingreso')),
            egresos=Sum('total', filter=Q(tipo_movimiento='Egreso')),
        )
        .order_by('-anio', '-mes')[:12]
    )
    for periodo in periodos:
        periodo['ingresos'] = periodo['ingresos'] or 0
        periodo['egresos'] = periodo['egresos'] or 0
        periodo['balance'] = periodo['ingresos'] - periodo['egresos']
        comparativo.append(periodo)

    return render(request, 'finanzas.html', {
        'finanza': finanza,
        'ingresos': ingresos,
        'egresos': egresos,
        'balance': balance,
        'por_categoria': por_categoria,
        'por_periodo': por_periodo,
        'comparativo': comparativo,
        'selected_year': selected_year or '',
        'selected_month': selected_month or '',
        'months': Finanza.MES_CHOICES,
    })


@login_required
def create_finanza(request):
    if request.method == 'POST':
        form = FinanzaForm(request.POST)
        if form.is_valid():
            finanza = form.save(commit=False)
            finanza.user = request.user
            finanza.save()
            return redirect('finanzas')
        return render(request, 'create_finanza.html', {
            'form': form,
            'error': 'Por favor provee un dato valido',
        })

    return render(request, 'create_finanza.html', {'form': FinanzaForm()})


@login_required
def delete_finanza(request, finanza_id):
    if request.method != 'POST':
        return redirect('finanzas')

    if request.user.is_superuser:
        finanza = get_object_or_404(Finanza, pk=finanza_id)
    else:
        finanza = get_object_or_404(Finanza, pk=finanza_id, user=request.user)
    finanza.delete()
    return redirect('finanzas')


@login_required
def finanza_detail(request, finanza_id):
    finanza = get_object_or_404(Finanza, pk=finanza_id)
    form = FinanzaForm(instance=finanza)

    if request.method == 'POST':
        form = FinanzaForm(request.POST, instance=finanza)
        if form.is_valid():
            form.save()
            return redirect('finanzas')

    show_form = request.GET.get('edit') == 'true' or request.method == 'POST'
    return render(request, 'finanza_detail.html', {
        'finanza': finanza,
        'form': form,
        'edit_mode': show_form,
    })


@login_required
def areas(request):
    ensure_default_areas(request.user)
    area = Area.objects.all().order_by('numero_piso', 'nombre')
    pisos = Area.objects.values('numero_piso').distinct().order_by('numero_piso')
    tipos_area = Area.objects.values('tipo_area').distinct().order_by('tipo_area')
    return render(request, 'areas.html', {
        'area': area,
        'pisos': [p['numero_piso'] for p in pisos if p['numero_piso'] is not None],
        'tipos_area': [t['tipo_area'] for t in tipos_area if t['tipo_area']],
    })


@login_required
def create_area(request):
    ensure_default_areas(request.user)
    if request.method == 'POST':
        form = AreaForm(request.POST)
        if form.is_valid():
            area = form.save(commit=False)
            area.user = request.user
            area.save()
            return redirect('areas')
        return render(request, 'create_area.html', {
            'form': form,
            'error': 'Por favor provee un dato valido',
        })

    form = AreaForm()
    if len(form.fields['nombre'].choices) <= 1:
        messages.info(request, 'Todas las areas fijas ya estan activas. Puedes editar su estado desde el detalle.')
        return redirect('areas')
    return render(request, 'create_area.html', {'form': form})


@login_required
def area_detail(request, area_id):
    area = get_object_or_404(Area, pk=area_id)
    form = AreaForm(instance=area)

    if request.method == 'POST':
        form = AreaForm(request.POST, instance=area)
        if form.is_valid():
            form.save()
            return redirect('areas')

    show_form = request.GET.get('edit') == 'true' or request.method == 'POST'
    return render(request, 'area_detail.html', {
        'area': area,
        'form': form,
        'edit_mode': show_form,
    })


@login_required
def delete_area(request, area_id):
    if request.method != 'POST':
        return redirect('areas')

    if request.user.is_superuser:
        area = get_object_or_404(Area, pk=area_id)
    else:
        area = get_object_or_404(Area, pk=area_id, user=request.user)
    if area.nombre in DEFAULT_AREA_NAMES:
        messages.warning(request, 'Esta area pertenece al catalogo fijo y no se puede eliminar.')
        return redirect('area_detail', area_id=area.id)
    area.delete()
    return redirect('areas')


@login_required
def backup_database(request):
    message = None
    if request.method == 'POST':
        result = os.system('python manage.py backup_db')
        message = 'Respaldo exitoso.' if result == 0 else 'Error al realizar el respaldo.'
    return render(request, 'bd.html', {'message': message})


@login_required
def restore_database(request):
    if request.method == 'POST':
        form = RestoreForm(request.POST, request.FILES)
        if form.is_valid():
            backup_file = request.FILES['backup_file']
            if not backup_file.name.endswith('.sqlite3'):
                return JsonResponse({'error': 'Por favor, selecciona un archivo con extension .sqlite3.'}, status=400)

            with open('db.sqlite3', 'wb') as db_file:
                db_file.write(backup_file.read())
            return JsonResponse({'message': 'La base de datos se restauro correctamente.'})
    else:
        form = RestoreForm()

    return render(request, 'restore.html', {'form': form})


@login_required
def calendario(request):
    return cleaning_schedule(request)


@login_required
def calendario_de_limpieza(request):
    return cleaning_reports(request)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def administracion(request):
    ensure_default_areas(request.user)
    hoy = timezone.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    inicio_mes = hoy.replace(day=1)
    siguiente_mes = inicio_mes.replace(year=inicio_mes.year + 1, month=1) if inicio_mes.month == 12 else inicio_mes.replace(month=inicio_mes.month + 1)
    fin_mes = siguiente_mes - timedelta(days=1)

    finanzas_semana = Finanza.objects.filter(fecha__range=[inicio_semana, fin_semana])
    finanzas_mes = Finanza.objects.filter(mes=hoy.month, anio=hoy.year)
    if not finanzas_mes.exists():
        finanzas_mes = Finanza.objects.filter(fecha__range=[inicio_mes, fin_mes])

    ingresos_mes = finanzas_mes.filter(tipo_movimiento='Ingreso').aggregate(total=Sum('total'))['total'] or 0
    egresos_mes = finanzas_mes.filter(tipo_movimiento='Egreso').aggregate(total=Sum('total'))['total'] or 0
    ingresos_semana = finanzas_semana.filter(tipo_movimiento='Ingreso').aggregate(total=Sum('total'))['total'] or 0
    egresos_semana = finanzas_semana.filter(tipo_movimiento='Egreso').aggregate(total=Sum('total'))['total'] or 0

    gastos_por_proveedor = finanzas_mes.filter(tipo_movimiento='Egreso').values('proveedor').annotate(
        total=Sum('total'), count=Count('id')
    ).exclude(proveedor__isnull=True).exclude(proveedor='').order_by('-total')[:5]

    mant_pendientes = Mantenimientos.objects.filter(~Q(estado='Completado')).count()
    mant_detenidos = Mantenimientos.objects.filter(estado='Detenido').count()
    mant_completados_semana = Mantenimientos.objects.filter(
        estado='Completado',
        fecha_completado__range=[inicio_semana, fin_semana],
    ).count()
    mant_por_prioridad = Mantenimientos.objects.values('prioridad').annotate(count=Count('id')).exclude(prioridad__isnull=True).exclude(prioridad='')
    mant_por_estado = Mantenimientos.objects.values('estado').annotate(count=Count('id')).exclude(estado__isnull=True).exclude(estado='')
    mant_por_tema = Mantenimientos.objects.values('titulo').annotate(count=Count('id')).exclude(titulo__isnull=True).exclude(titulo='').order_by('-count')[:8]

    limpieza_pendiente = Limpieza.objects.filter(estado='Pendiente').count()
    limpieza_completada_semana = Limpieza.objects.filter(
        estado='Completado',
        fecha_programada__range=[inicio_semana, fin_semana],
    ).count()
    limpieza_hoy = Limpieza.objects.filter(fecha_programada__date=hoy).order_by('fecha_programada')

    areas_ocupadas = Area.objects.filter(estado='Ocupado').count()
    areas_libres = Area.objects.filter(estado='Libre').count()
    areas_mantenimiento = Area.objects.filter(estado='En mantenimiento').count()
    total_areas = Area.objects.count()
    areas_por_estado = Area.objects.values('estado').annotate(count=Count('id')).exclude(estado__isnull=True).exclude(estado='')

    cleaning_activity_total = Activity.objects.count()
    cleaning_logs_week = CleaningLog.objects.filter(date__range=[inicio_semana, fin_semana])
    cleaning_completed_week = cleaning_logs_week.filter(completed=True).count()
    cleaning_completion_rate = round((cleaning_completed_week / cleaning_logs_week.count() * 100) if cleaning_logs_week.count() else 0)
    cleaning_by_area = cleaning_logs_week.filter(completed=True).values('activity__area').annotate(count=Count('id')).order_by('-count')[:8]

    context = {
        'total_gastos_semana': egresos_semana,
        'total_gastos_mes': egresos_mes,
        'ingresos_semana': ingresos_semana,
        'ingresos_mes': ingresos_mes,
        'egresos_mes': egresos_mes,
        'balance_mes': ingresos_mes - egresos_mes,
        'gastos_por_proveedor': gastos_por_proveedor,
        'mant_pendientes': mant_pendientes,
        'mant_detenidos': mant_detenidos,
        'mant_completados_semana': mant_completados_semana,
        'mant_por_prioridad': mant_por_prioridad,
        'mant_por_estado': mant_por_estado,
        'mant_por_tema': mant_por_tema,
        'limpieza_pendiente': limpieza_pendiente,
        'limpieza_completada_semana': limpieza_completada_semana,
        'limpieza_hoy': limpieza_hoy,
        'areas_ocupadas': areas_ocupadas,
        'areas_libres': areas_libres,
        'areas_mantenimiento': areas_mantenimiento,
        'total_areas': total_areas,
        'areas_por_estado': areas_por_estado,
        'cleaning_activity_total': cleaning_activity_total,
        'cleaning_completion_rate': cleaning_completion_rate,
        'cleaning_by_area': cleaning_by_area,
        'hoy': hoy,
        'inicio_semana': inicio_semana,
        'fin_semana': fin_semana,
        'nombre_mes': calendar.month_name[hoy.month],
    }
    return render(request, 'administracion.html', context)
