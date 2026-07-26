from django.urls import path
from . import views

urlpatterns = [
    path('library/', views.content_library, name='content_library'),
    path('submit/', views.content_submit, name='content_submit'),
    path('review/', views.content_review_queue, name='content_review_queue'),
    path('review/<slug:slug>/decide/', views.content_review_decide, name='content_review_decide'),
    path('content/<slug:slug>/', views.content_detail, name='content_detail'),
]
