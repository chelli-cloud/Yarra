from django.urls import path
from . import views

urlpatterns = [
    path('', views.vendor_list, name='vendor_list'),
    path('signup/', views.vendor_signup, name='vendor_signup'),
    path('<int:pk>/', views.vendor_detail, name='vendor_detail'),
    path('<int:vendor_id>/promotion/add/', views.vendor_promotion_create, name='vendor_promotion_create'),
]
