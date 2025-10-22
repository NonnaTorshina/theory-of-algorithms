from django.urls import path
from . import views

urlpatterns = [
    path('', views.sleep_records, name='sleep_records'),
    path('add/', views.add_record, name='add_record'),
    path('stats/', views.stats, name='stats'),
    path('api/sleep-records/', views.SleepRecordListCreate.as_view(), name='sleep-records-list'),
    path('api/sleep-records/<int:pk>/', views.SleepRecordDetail.as_view(), name='sleep-records-detail'),
]