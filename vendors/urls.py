from django.urls import path
from . import views

urlpatterns = [
    path('', views.vendor_list, name='vendor_list'),
    path('signup/', views.vendor_signup, name='vendor_signup'),
    path('<int:pk>/', views.vendor_detail, name='vendor_detail'),
    path('<int:vendor_id>/promotion/add/', views.vendor_promotion_create, name='vendor_promotion_create'),
    path('requests/mine/', views.my_requests, name='my_requests'),
    path('events/<int:event_pk>/interest/', views.event_interest_submit, name='event_interest_submit'),
]
