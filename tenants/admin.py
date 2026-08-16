from django.contrib import admin
from .models import (
    School, Profile, ReviewCycle, Notification, DiscussionThread, ThreadReply,
    Invitation, SchoolProfileExtended, SchoolDocument, Payment, ActivityLog,
    YarraEvaluator, EvaluatorQuery, SelfEvaluationResponse, SelfEvaluationFile,
)

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'contact_person', 'email', 'phone')
    search_fields = ('name', 'location', 'email')

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


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'school', 'role', 'is_used', 'created_at')
    list_filter = ('role', 'is_used')
    search_fields = ('email', 'school__name')


@admin.register(SchoolProfileExtended)
class SchoolProfileExtendedAdmin(admin.ModelAdmin):
    list_display = ('school', 'curriculum_adopted', 'updated_at')
    search_fields = ('school__name',)


@admin.register(SchoolDocument)
class SchoolDocumentAdmin(admin.ModelAdmin):
    list_display = ('school', 'file', 'uploaded_by', 'uploaded_at')
    list_filter = ('school',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('school', 'amount', 'method', 'recorded_by', 'created_at')
    list_filter = ('method',)
    search_fields = ('school__name',)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'description', 'created_at')
    list_filter = ('school',)
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at',)


@admin.register(YarraEvaluator)
class YarraEvaluatorAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'user__email')


@admin.register(EvaluatorQuery)
class EvaluatorQueryAdmin(admin.ModelAdmin):
    list_display = ('review_cycle', 'evaluator', 'created_at', 'answered_at')
    list_filter = ('evaluator',)
    search_fields = ('question', 'answer', 'review_cycle__school__name')


@admin.register(SelfEvaluationResponse)
class SelfEvaluationResponseAdmin(admin.ModelAdmin):
    list_display = ('review_cycle', 'updated_by', 'updated_at')
    search_fields = ('review_cycle__school__name',)


@admin.register(SelfEvaluationFile)
class SelfEvaluationFileAdmin(admin.ModelAdmin):
    list_display = ('review_cycle', 'question_id', 'uploaded_at')
    list_filter = ('question_id',)
    search_fields = ('review_cycle__school__name', 'question_id')
