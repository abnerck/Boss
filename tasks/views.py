from django.http import HttpResponse
from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import MantenimientoForm, LimpiezaForm, FinanzaForm , RestoreForm, AreaForm
from .models import Mantenimientos, Limpieza, Finanza, Area
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import PasswordResetView
import os
from django.shortcuts import render
from django.http import JsonResponse

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from cleaning.views import cleaning_schedule ,cleaning_reports
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import calendar


def password_reset_view(request):
    return PasswordResetView.as_view()(request)

def home(request):
    return render(request, 'home.html')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm(),
        })
    else:
        # Validar que el email fue proporcionado
        email = request.POST.get('email', '').strip()
        if not email:
            return render(request, 'signup.html', {
                'form': UserCreationForm(),
                'error': 'El correo electrónico es obligatorio'
            })
        
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    email=email,
                    password=request.POST['password1']
                )
                user.save()
                login(request, user)
                return redirect('mantenimientos')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm(),
                    'error': 'El usuario ya existe'
                })
        else:
            return render(request, 'signup.html', {
                'form': UserCreationForm(),
                'error': 'Las contraseñas no coinciden'
            })


def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':

        return render(request,'signin.html',{
            'form':AuthenticationForm,
        })
    else:
        user = authenticate(request, username=request.POST['username'],password=request.POST['password'])

        if user is None:
            return render(request,'signin.html',{
            'form':AuthenticationForm,
            'error':'Usuario o contraseña es incorrecta'
        })
        else:
            login(request,user)
            return redirect('mantenimientos')

@login_required
def mantenimientos(request):

    
    mantenimiento = Mantenimientos.objects.all()
    return render(request, 'mantenimientos.html',{
        'mantenimiento':mantenimiento,
        
    })

@login_required
def create_mantenimientos(request):
    if request.method == 'POST':
        print("Método:", request.method)
        print("Usuario autenticado:", request.user.is_authenticated)
        print("CSRF Token recibido:", request.POST.get('csrfmiddlewaretoken'))
        print("Datos enviados:", request.POST)
        print("Archivos enviados:", request.FILES)
        form = MantenimientoForm(request.POST, request.FILES)
        if form.is_valid():
            mantenimiento = form.save(commit=False)
            mantenimiento.user = request.user
            mantenimiento.save()
            messages.success(request, 'Mantenimiento registrado con éxito.')
            return redirect('/mantenimientos/')
        else:
            print("Errores del formulario:", form.errors)
            return render(request, 'create_mantenimientos.html', {
                'form': form,
                'error': f'Error en el formulario: {form.errors.as_text()}'
            })
    else:
        form = MantenimientoForm()
    return render(request, 'create_mantenimientos.html', {'form': form})


@login_required
def mantenimientos_detail(request, mantenimiento_id):
    mantenimiento = get_object_or_404(Mantenimientos, pk=mantenimiento_id)
    form = MantenimientoForm(instance=mantenimiento)
    
    if request.method == 'POST':
        form = MantenimientoForm(request.POST, instance=mantenimiento)
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
def delete_mantenimientos(request,mantenimiento_id):
    if request.user.is_superuser:
        mantenimientos = get_object_or_404(Mantenimientos,pk=mantenimiento_id)
        mantenimientos.delete()
        return redirect('mantenimientos')
    else:
        producto = get_object_or_404(Mantenimientos, pk=mantenimiento_id, user=request.user)
        if request.method == 'POST':
            producto.delete()
            return redirect('mantenimientos')

##########
@login_required
def limpiezas(request):
    
    
    limpiezas_list = Limpieza.objects.all()
    
    return render(request, 'limpiezas.html', {
        'limpiezas': limpiezas_list,
    })

@login_required
def create_limpiezas(request):

    if request.method == 'GET':
        return render(request,'create_limpieza.html',{
            'form':LimpiezaForm
        })
    else:
        try:
            form = LimpiezaForm(request.POST)
            newlimpieza = form.save(commit=False)
            newlimpieza.user = request.user
            newlimpieza.save()
            return redirect('limpiezas')
        except ValueError:
            return render(request,'create_limpieza.html',{
            'form':LimpiezaForm,
            'error':'Porfavor Provee un dato valido'
        })

@login_required
def limpiezas_detail(request, limpieza_id):
    limpieza = get_object_or_404(Limpieza,pk=limpieza_id)
    show_form = request.GET.get('edit') == 'true'

    if request.method == 'POST':
        form = LimpiezaForm(request.POST, instance=limpieza)
        if form.is_valid():
            form.save()
            return redirect('limpiezas')
    else:
        form = LimpiezaForm(instance=limpieza)

    
    return render(request, 'limpiezas_detail.html', {
        'limpieza': limpieza,
        'form': form,
        'show_form': show_form,
    })

@login_required
def delete_limpieza(request, limpieza_id):
    if request.method == 'POST':
        if request.user.is_superuser:
            limpieza = get_object_or_404(Limpieza, pk=limpieza_id)
        else:
            limpieza = get_object_or_404(Limpieza, pk=limpieza_id, user=request.user)
        
        limpieza.delete()
        return redirect('limpiezas')
    
    # Si alguien intenta acceder por GET, lo rediriges para evitar eliminar por URL
    return redirect('limpiezas')

@login_required
def usuarios(request):
    
    
    lista_usuarios = User.objects.all()
    
    return render(request, 'usuarios.html', {
        'usuarios': lista_usuarios,
    })

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

    finanza = Finanza.objects.all()
    return render(request, 'finanzas.html',{
        'finanza':finanza,
    })

def create_finanza(request):
    if request.method == 'GET':
        return render(request,'create_finanza.html',{
            'form':FinanzaForm
        })
    else:
        try:
            form = FinanzaForm(request.POST)
            newfinanza = form.save(commit=False)
            newfinanza.user = request.user
            newfinanza.save()
            return redirect('finanzas')
        except ValueError:
            return render(request,'create_finanza.html',{
            'form':FinanzaForm,
            'error':'Porfavor Provee un dato valido'
        })

@login_required
def delete_finanza(request, finanza_id):
    if request.method == 'POST':
        if request.user.is_superuser:
            finanza = get_object_or_404(Finanza, pk=finanza_id)
        else:
            finanza = get_object_or_404(Finanza, pk=finanza_id, user=request.user)
        
        finanza.delete()
        return redirect('finanzas')
    
    # Si alguien intenta acceder por GET, lo rediriges para evitar eliminar por URL
    return redirect('finanzas')

@login_required
def finanza_detail(request, finanza_id):
    finanza = get_object_or_404(Finanza,pk=finanza_id)
    

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
    area = Area.objects.all()
    pisos = Area.objects.values('numero_piso').distinct().order_by('numero_piso')
    tipos_area = Area.objects.values('tipo_area').distinct().order_by('tipo_area')
    return render(request, 'areas.html', {
        'area': area,
        'pisos': [p['numero_piso'] for p in pisos if p['numero_piso']],
        'tipos_area': [t['tipo_area'] for t in tipos_area if t['tipo_area']]
    })

@login_required
def create_area(request):
    if request.method == 'GET':
        return render(request, 'create_area.html', {
            'form': AreaForm()
        })
    else:
        try:
            form = AreaForm(request.POST)
            if form.is_valid():
                newarea = form.save(commit=False)
                newarea.user = request.user
                newarea.save()
                return redirect('areas')
            else:
                raise ValueError("Formulario inválido")
        except ValueError:
            return render(request, 'create_area.html', {
                'form': AreaForm(request.POST),
                'error': 'Por favor provee un dato válido'
            })

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
    if request.method == 'POST':
        if request.user.is_superuser:
            area = get_object_or_404(Area, pk=area_id)
        else:
            area = get_object_or_404(Area, pk=area_id, user=request.user)
        
        area.delete()
        return redirect('areas')
    
    return redirect('areas')


@login_required
def backup_database(request):
    message = None  # Inicializa el mensaje como None

    if request.method == 'POST':
        # Ejecuta el comando de respaldo
        result = os.system('python manage.py backup_db')
        if result == 0:
            message = 'Respaldo exitoso.'
            respaldo_exitoso = True
        else:
            message = 'Error al realizar el respaldo.'

    return render(request, 'bd.html', {'message': message})

@login_required
def restore_database(request):
    if request.method == 'POST':
        form = RestoreForm(request.POST, request.FILES)
        if form.is_valid():
            backup_file = request.FILES['backup_file']
            
            # Verifica si la extensión del archivo es ".sqlite3"
            if not backup_file.name.endswith('.sqlite3'):
                return JsonResponse({'error': 'Por favor, selecciona un archivo con extensión .sqlite3.'}, status=400)

            backup_data = backup_file.read()  # Lee los datos del archivo

            # Guarda los datos del respaldo en el archivo de la base de datos
            with open('db.sqlite3', 'wb') as db_file:
                db_file.write(backup_data)

            return JsonResponse({'message': 'La base de datos se restauró correctamente.'})

    else:
        form = RestoreForm()

    return render(request, 'restore.html', {'form': form})

@login_required
def calendario(request):

    response = cleaning_schedule(request)
    return(response)

@login_required
def calendario_de_limpieza(request):

    response = cleaning_reports (request)

    return(response)





@login_required
@user_passes_test(lambda u: u.is_superuser)  # Solo admins
def administracion(request):
    hoy = timezone.now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes
    fin_semana = inicio_semana + timedelta(days=6)
    inicio_mes = hoy.replace(day=1)
    fin_mes = inicio_mes.replace(month=inicio_mes.month % 12 + 1, day=1) - timedelta(days=1)

    # === FINANZAS ===
    finanzas_semana = Finanza.objects.filter(fecha__range=[inicio_semana, fin_semana])
    finanzas_mes = Finanza.objects.filter(fecha__range=[inicio_mes, fin_mes])

    total_semana = finanzas_semana.aggregate(total=Sum('total'))['total'] or 0
    total_mes = finanzas_mes.aggregate(total=Sum('total'))['total'] or 0

    gastos_por_proveedor = finanzas_mes.values('proveedor').annotate(
        total=Sum('total'), count=Count('id')
    ).exclude(proveedor__isnull=True).exclude(proveedor='')[:5]

    # === MANTENIMIENTOS ===
    mant_pendientes = Mantenimientos.objects.filter(~Q(estado="Completado")).count()
    mant_completados_semana = Mantenimientos.objects.filter(
        estado="Completado", fecha_completado__range=[inicio_semana, fin_semana]
    ).count()

    mant_por_prioridad = Mantenimientos.objects.values('prioridad').annotate(
        count=Count('id')
    ).exclude(prioridad__isnull=True).exclude(prioridad='')

    # === LIMPIEZA ===
    limpieza_pendiente = Limpieza.objects.filter(estado='Pendiente').count()
    limpieza_completada_semana = Limpieza.objects.filter(
        estado='Completado', fecha_programada__range=[inicio_semana, fin_semana]
    ).count()

    limpieza_hoy = Limpieza.objects.filter(
        fecha_programada__date=hoy
    ).order_by('fecha_programada')

    # === ÁREAS ===
    areas_ocupadas = Area.objects.filter(estado="Ocupado").count()
    areas_libres = Area.objects.filter(estado="Libre").count()
    total_areas = Area.objects.count()

    context = {
        # Finanzas
        'total_gastos_semana': total_semana,
        'total_gastos_mes': total_mes,
        'gastos_por_proveedor': gastos_por_proveedor,

        # Mantenimientos
        'mant_pendientes': mant_pendientes,
        'mant_completados_semana': mant_completados_semana,
        'mant_por_prioridad': mant_por_prioridad,

        # Limpieza
        'limpieza_pendiente': limpieza_pendiente,
        'limpieza_completada_semana': limpieza_completada_semana,
        'limpieza_hoy': limpieza_hoy,

        # Áreas
        'areas_ocupadas': areas_ocupadas,
        'areas_libres': areas_libres,
        'total_areas': total_areas,

        # Fechas
        'hoy': hoy,
        'inicio_semana': inicio_semana,
        'fin_semana': fin_semana,
        'nombre_mes': calendar.month_name[hoy.month],
    }

    return render(request, 'administracion.html', context)