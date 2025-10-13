from django.contrib import admin
from django.urls import path, include
from tasks import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home,name='home'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),

    path('areas/', views.areas, name='areas'),
    path('areas/create/', views.create_area, name='create_area'),
    path('areas/<int:area_id>/', views.area_detail, name='area_detail'),
    path('area/<int:area_id>/delete/', views.delete_area, name='delete_area'),

    path('mantenimientos/', views.mantenimientos, name='mantenimientos'),
    path('mantenimientos/create/', views.create_mantenimientos, name='create_mantenimientos'),
    path('mantenimientos/<int:mantenimiento_id>/', views.mantenimientos_detail, name='mantenimientos_detail'),
    path('mantenimientos/<int:mantenimiento_id>/delete/', views.delete_mantenimientos, name='delete_mantenimiento'),

    path('limpiezas/', views.limpiezas, name='limpiezas'),
    path('limpiezas/create/', views.create_limpiezas, name='create_limpiezas'),
    path('limpiezas/<int:limpieza_id>/', views.limpiezas_detail, name='limpieza_detail'),
    path('limpiezas/<int:limpieza_id>/delete/', views.delete_limpieza, name='delete_limpieza'),

    path('finanzas/', views.finanzas, name='finanzas'),
    path('finanzas/create/', views.create_finanza, name='create_finanza'),
    path('finanza/<int:finanza_id>/', views.finanza_detail, name='finanza_detail'),
    path('finanzas/<int:finanza_id>/delete/', views.delete_finanza, name='delete_finanza'),
    
    
    path('usuarios/', views.usuarios, name='usuarios'),
    path('usuarios/create/', views.create_usuario, name='create_usuario'),
    path('usuarios/<int:usuario_id>/delete/', views.delete_usuario, name='delete_usuario'),


    
    
    path('calendario/', views.calendario, name='calendario'),
    path('calendario/Reprtes/', views.calendario_de_limpieza, name='reportes_de_limpieza'),
    
    

    # 1. Formulario de recuperación
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    # 2. Confirmación de envío de email
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),

    # 3. Confirmación con token
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # 4. Confirmación final
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # RESPALDO BD
    path('respaldo/', views.backup_database, name='bd'),
    path('restore/', views.restore_database, name='restore'),

    path('cleaning/', include('cleaning.urls')),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)