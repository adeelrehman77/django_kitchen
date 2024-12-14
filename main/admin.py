
from django.contrib import admin
from django.utils.html import format_html
from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active', 'image_preview')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Image'

@admin.register(MenuList)
class MenuListAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    filter_horizontal = ('items',)

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('get_slot_name', 'start_time', 'end_time')
    list_filter = ('name',)
    
    def get_slot_name(self, obj):
        if obj.name == 'custom' and obj.custom_name:
            return obj.custom_name
        return obj.get_name_display()
    get_slot_name.short_description = 'Slot Name'

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'zone', 'route', 'building_name', 'is_active')
    list_filter = ('zone', 'route', 'is_active', 'preferred_payment')
    search_fields = ('user__username', 'user__first_name', 'phone', 'building_name', 'flat_number')
    raw_id_fields = ('user',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'phone', 'is_active')
        }),
        ('Location Details', {
            'fields': ('zone', 'route', 'building_name', 'flat_number', 'floor_number', 'landmark')
        }),
        ('Payment Information', {
            'fields': ('preferred_payment',)
        })
    )

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'menu', 'start_date', 'end_date', 'payment_mode')
    list_filter = ('payment_mode', 'time_slot')

@admin.register(Hub)
class HubAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_number', 'is_active')
    search_fields = ('name', 'address')
    list_filter = ('is_active',)

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'hub', 'is_active')
    list_filter = ('hub', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone', 'estimated_delivery_time', 'is_active')
    list_filter = ('zone__hub', 'zone', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'license_number', 'assigned_route', 'is_active')
    list_filter = ('is_active', 'assigned_route__zone__hub')
    search_fields = ('user__username', 'license_number', 'phone')
    raw_id_fields = ('user',)

@admin.register(DeliveryStatus)
class DeliveryStatusAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'date', 'status')
    list_filter = ('status', 'date')
