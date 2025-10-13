from django.urls import path
from . import views

urlpatterns = [
    path('', views.cleaning_schedule, name='cleaning_schedule'),
    path('save/', views.save_log, name='save_log'),
    path('reports/', views.cleaning_reports, name='cleaning_reports'),
]