from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='home'),
    path('tsp-algorythm', views.tsp_algorythm, name='tsp-algorythm'),
    path('history', views.history, name='history')


]
