from django.urls import path
from . import views
from .webhooks import razorpay_webhook

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('opportunities/', views.opportunity_list, name='opportunity_list'),
    path('create/', views.event_create, name='event_create'),
    path('analytics/', views.sl_analytics, name='sl_analytics'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('notifications/read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('webhooks/razorpay/', razorpay_webhook, name='razorpay_webhook'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('<int:pk>/register/', views.register_for_event, name='register_for_event'),
    path('registration/<int:pk>/confirm/', views.registration_confirm, name='registration_confirm'),
    path('registration/<int:pk>/attendance/', views.mark_attendance, name='mark_attendance'),
    path('registration/<int:pk>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('registration/<int:pk>/invoice/', views.download_invoice, name='download_invoice'),
    path('<int:event_pk>/result/', views.create_competition_result, name='create_competition_result'),
]
