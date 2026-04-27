from django.urls import path
from . import views

urlpatterns = [
    path('', views.exchange_list, name='exchange_list'),
    path('<int:pk>/', views.exchange_detail, name='exchange_detail'),
    path('my/', views.my_exchanges, name='my_exchanges'),
    path('create/', views.create_listing, name='create_listing'),
    path('application/<int:pk>/', views.application_detail, name='application_detail'),
    path('application/<int:pk>/complete/', views.complete_exchange, name='complete_exchange'),
    path('application/<int:pk>/feedback/', views.submit_exchange_feedback, name='submit_exchange_feedback'),
]
