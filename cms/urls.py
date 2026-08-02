from django.urls import path
from . import views

urlpatterns = [
    path('library/', views.content_library, name='content_library'),
    path('submit/', views.content_submit, name='content_submit'),
    path('review/', views.content_review_queue, name='content_review_queue'),
    path('review/<slug:slug>/decide/', views.content_review_decide, name='content_review_decide'),
    path('bookmarks/', views.my_bookmarks, name='my_bookmarks'),
    path('content/<slug:slug>/', views.content_detail, name='content_detail'),
    path('content/<slug:slug>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('comment/<int:comment_id>/like/', views.toggle_comment_like, name='toggle_comment_like'),
    path('comment/<int:comment_id>/flag/', views.flag_comment, name='flag_comment'),
]
