from django.contrib import admin
from .models import Category, Tag, ContentItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'status', 'publish_at', 'is_early_years_only')
    list_filter = ('content_type', 'status', 'is_early_years_only', 'category')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags', 'target_schools')
