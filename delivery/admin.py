
from django.contrib import admin
from .models import Hub, Zone, Route, Driver
from import_export import resources
from import_export.admin import ImportExportModelAdmin

class HubAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'contact_number', 'capacity', 'operating_hours', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code', 'address')
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'address', 'is_active')
        }),
        ('Contact Details', {
            'fields': ('contact_number', 'email')
        }),
        ('Operations', {
            'fields': ('capacity', 'operating_hours')
        })
    )

class ZoneAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'hub', 'delivery_charge', 'min_delivery_time', 'is_active')
    list_filter = ('hub', 'is_active')
    search_fields = ('name', 'code', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'hub', 'is_active')
        }),
        ('Details', {
            'fields': ('description', 'coverage_area')
        }),
        ('Delivery Settings', {
            'fields': ('delivery_charge', 'min_delivery_time')
        })
    )

class RouteAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'zone', 'priority', 'estimated_delivery_time', 'max_orders', 'is_active')
    list_filter = ('zone__hub', 'zone', 'priority', 'is_active')
    search_fields = ('name', 'code', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'zone', 'is_active')
        }),
        ('Route Details', {
            'fields': ('description', 'priority', 'start_location', 'end_location')
        }),
        ('Capacity Settings', {
            'fields': ('estimated_delivery_time', 'max_orders')
        })
    )

class DriverResource(resources.ModelResource):
    class Meta:
        model = Driver
        fields = ('user__username', 'employee_id', 'phone', 'alternate_phone', 
                 'license_number', 'vehicle_type', 'vehicle_number', 
                 'assigned_route', 'joining_date', 'is_active')

class DriverAdmin(ImportExportModelAdmin):
    resource_class = DriverResource
    list_display = ('user', 'phone', 'license_number', 'assigned_route', 'is_active')
    list_filter = ('is_active', 'assigned_route__zone__hub')
    search_fields = ('user__username', 'user__first_name', 'license_number')

admin.site.register(Hub, HubAdmin)
admin.site.register(Zone, ZoneAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(Driver, DriverAdmin)
