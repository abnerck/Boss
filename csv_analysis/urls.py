from django.urls import path

from . import views

app_name = 'csv_analysis'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_csv, name='upload'),
    path('ask/', views.ask_ai, name='ask'),
    path('delete/<int:upload_id>/', views.delete_upload, name='delete'),
]
