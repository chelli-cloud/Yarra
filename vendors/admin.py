from django.contrib import admin
from .models import Vendor, VendorPromotion

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_vetted', 'is_approved', 'created_at')
    list_filter = ('category', 'is_vetted', 'is_approved')
    search_fields = ('name', 'description')
    actions = ['approve_vendors', 'vett_vendors']

    def approve_vendors(self, request, queryset):
        queryset.update(is_approved=True)
    approve_vendors.short_description = "Approve selected vendors"

    def vett_vendors(self, request, queryset):
        queryset.update(is_vetted=True)
    vett_vendors.short_description = "Mark selected vendors as vetted"

@admin.register(VendorPromotion)
class VendorPromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'vendor', 'placement', 'start_date', 'end_date', 'is_approved')
    list_filter = ('placement', 'is_approved', 'start_date', 'end_date')
    search_fields = ('title', 'vendor__name')
    actions = ['approve_promotions']

    def approve_promotions(self, request, queryset):
        queryset.update(is_approved=True)
    approve_promotions.short_description = "Approve selected promotions"
