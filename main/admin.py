
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
    list_display = ('user', 'phone', 'zone', 'route', 'building_name', 'active_subscription', 'get_subscription_stats')
    list_filter = ('zone', 'route')
    search_fields = ('user__username', 'phone', 'building_name', 'flat_number')
    raw_id_fields = ('user',)

    def get_subscription_stats(self, obj):
        total_subs = obj.subscription_set.count()
        active_subs = obj.subscription_set.filter(end_date__gte=datetime.date.today()).count()
        return f"Active: {active_subs} | Total: {total_subs}"
    get_subscription_stats.short_description = 'Subscription Stats'

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'menu', 'start_date', 'end_date', 'payment_mode', 'get_delivery_stats')
    list_filter = ('payment_mode', 'time_slot', 'start_date', 'end_date')
    search_fields = ('customer__user__username', 'menu__name')
    
    def get_delivery_stats(self, obj):
        total = obj.deliverystatus_set.count()
        delivered = obj.deliverystatus_set.filter(status='delivered').count()
        pending = obj.deliverystatus_set.filter(status='pending').count()
        return f"Total: {total} | Delivered: {delivered} | Pending: {pending}"
    get_delivery_stats.short_description = 'Delivery Stats'

@admin.register(DeliveryStatus)
class DeliveryStatusAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'date', 'status', 'customer_name', 'menu_name')
    list_filter = ('status', 'date', 'subscription__menu')
    search_fields = ('subscription__customer__user__username', 'subscription__menu__name')
    date_hierarchy = 'date'

    def customer_name(self, obj):
        return obj.subscription.customer.user.username
    customer_name.short_description = 'Customer'

    def menu_name(self, obj):
        return obj.subscription.menu.name
    menu_name.short_description = 'Menu'
