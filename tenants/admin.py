from django.contrib import admin
from .models import School, Profile, ReviewCycle, Notification, TeacherResource, DiscussionThread, ThreadReply

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'contact_person', 'email', 'phone')
    search_fields = ('name', 'location', 'email')

@admin.register(TeacherResource)
class TeacherResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'school', 'uploaded_by', 'created_at')
    list_filter = ('school',)
    search_fields = ('title', 'school__name')

@admin.register(DiscussionThread)
class DiscussionThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'is_locked', 'created_at')
    list_filter = ('is_locked',)
    search_fields = ('title', 'created_by__username')

@admin.register(ThreadReply)
class ThreadReplyAdmin(admin.ModelAdmin):
    list_display = ('author', 'thread', 'posted_at')
    search_fields = ('content', 'author__username', 'thread__title')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'school__name')

@admin.register(ReviewCycle)
class ReviewCycleAdmin(admin.ModelAdmin):
    list_display = ('school', 'title', 'created_at')
    list_filter = ('school',)
    search_fields = ('title', 'school__name')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'title', 'level', 'is_read', 'created_at')
    list_filter = ('level', 'is_read')
    search_fields = ('recipient__username', 'title', 'message')
    readonly_fields = ('created_at',)
