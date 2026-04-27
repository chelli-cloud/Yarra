from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('school-profile/', views.school_profile, name='school_profile'),
    path('school-profile/<int:pk>/', views.school_profile, name='school_profile_detail'),
    path('master/', views.master_dashboard, name='master_dashboard'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('school-review/', views.review_dashboard, name='review_dashboard'),
    path('school-review/create/', views.create_review_cycle, name='create_review_cycle'),
    path('teachers-hub/', views.teachers_hub, name='teachers_hub'),
    path('network/', views.school_network, name='school_network'),
    path('leadership/', views.leadership_connect, name='leadership_connect'),
    path('leadership/thread/<int:pk>/', views.thread_detail, name='thread_detail'),
    path('invite/', views.invite_user, name='invite_user'),
    path('invite/accept/<str:token>/', views.accept_invitation, name='accept_invitation'),
    path('register-school/', views.school_registration, name='school_registration'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
]
