from django.contrib import admin
from .models import User, Status, Service, Report

@admin.register(User)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('tg_id', )

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'status_name')
    search_fields = ('name', 'status__name')
    
    def status_name(self, obj):
        return obj.status.name
    status_name.admin_order_field = 'status'
    status_name.short_description = 'Status Name'

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('time', 'provider_value', 'status_name', 'services_list', 'is_vpn_used')
    search_fields = ('provider_value', 'region_value', 'status__name', 'services__name')
    
    def status_name(self, obj):
        return obj.status.name if obj.status else 'N/A'
    status_name.short_description = 'Status'
    
    def services_list(self, obj):
        return ", ".join([service.name for service in obj.services.all()])
    services_list.short_description = 'Services'
    