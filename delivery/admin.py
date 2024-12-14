
from django.contrib import admin
from .models import Hub, Zone, Route, Driver
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class HubAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_number', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')

class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'hub', 'is_active')
    list_filter = ('hub', 'is_active')
    search_fields = ('name', 'description')

class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone', 'estimated_delivery_time', 'is_active')
    list_filter = ('zone__hub', 'zone', 'is_active')
    search_fields = ('name', 'description')

class DriverResource(resources.ModelResource):
    class Meta:
        model = Driver
        fields = ('user__username', 'phone', 'license_number', 'assigned_route', 'is_active')

class DriverAdmin(ImportExportModelAdmin):
    resource_class = DriverResource
    list_display = ('user', 'phone', 'license_number', 'assigned_route', 'is_active')
    list_filter = ('is_active', 'assigned_route__zone__hub')
    search_fields = ('user__username', 'user__first_name', 'license_number')

admin.site.register(Hub, HubAdmin)
admin.site.register(Zone, ZoneAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(Driver, DriverAdmin)
