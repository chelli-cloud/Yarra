"""
URL configuration for yarra project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from tenants.admin_views import (
    admin_dashboard, export_schools_csv, export_payments_csv, export_vendors_csv,
    broadcast_announcement,
)

urlpatterns = [
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/dashboard/export/schools/', export_schools_csv, name='export_schools_csv'),
    path('admin/dashboard/export/payments/', export_payments_csv, name='export_payments_csv'),
    path('admin/dashboard/export/vendors/', export_vendors_csv, name='export_vendors_csv'),
    path('admin/dashboard/broadcast/', broadcast_announcement, name='broadcast_announcement'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('vendors/', include('vendors.urls')),
    path('exchanges/', include('exchanges.urls')),
    path('', include('tenants.urls')),
    path('competitions/', include('competitions.urls')),
    path('cms/', include('cms.urls')),
    path('analytics/', include('analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
