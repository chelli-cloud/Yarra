from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.consortium_dashboard, name='consortium_dashboard'),
]
