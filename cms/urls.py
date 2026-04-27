from django.urls import path
from . import views

urlpatterns = [
    path('library/', views.content_library, name='content_library'),
    path('content/<slug:slug>/', views.content_detail, name='content_detail'),
]
