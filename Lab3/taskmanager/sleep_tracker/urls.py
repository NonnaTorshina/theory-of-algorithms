from django.urls import path
from . import views

urlpatterns = [
    path('', views.sleep_records, name='sleep_records'),
    path('add/', views.add_record, name='add_record'),
    path('stats/', views.stats, name='stats'),
]