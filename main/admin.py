
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
    list_display = ('user', 'phone', 'zone', 'route', 'building_name', 'active_subscription', 'get_subscription_stats', 'get_delivery_stats')
    list_filter = ('zone', 'route', 'subscription__payment_mode')
    search_fields = ('user__username', 'phone', 'building_name', 'flat_number')
    raw_id_fields = ('user',)
    actions = ['download_customer_report']

    def get_subscription_stats(self, obj):
        total_subs = obj.subscription_set.count()
        active_subs = obj.subscription_set.filter(end_date__gte=datetime.date.today()).count()
        return f"Active: {active_subs} | Total: {total_subs}"
    get_subscription_stats.short_description = 'Subscription Stats'

    def get_delivery_stats(self, obj):
        total = DeliveryStatus.objects.filter(subscription__customer=obj).count()
        delivered = DeliveryStatus.objects.filter(subscription__customer=obj, status='delivered').count()
        if total:
            return f"{delivered}/{total} ({int((delivered/total)*100)}%)"
        return "No deliveries"
    get_delivery_stats.short_description = 'Delivery Success'

    def download_customer_report(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="customer_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Customer', 'Phone', 'Zone', 'Route', 'Address', 'Active Subscriptions', 'Total Deliveries'])
        
        for profile in queryset:
            writer.writerow([
                profile.user.username,
                profile.phone,
                profile.zone,
                profile.route,
                profile.full_address,
                profile.subscription_set.filter(end_date__gte=datetime.date.today()).count(),
                DeliveryStatus.objects.filter(subscription__customer=profile).count()
            ])
        return response
    download_customer_report.short_description = "Download Customer Report"

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
    list_filter = ('status', 'date', 'subscription__menu', 'subscription__customer__zone', 'subscription__customer__route')
    search_fields = ('subscription__customer__user__username', 'subscription__menu__name')
    date_hierarchy = 'date'
    actions = ['mark_as_delivered', 'mark_as_cancelled']

    def zone(self, obj):
        return obj.subscription.customer.zone
    
    def route(self, obj):
        return obj.subscription.customer.route

    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = "Mark selected as delivered"

    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "Mark selected as cancelled"

    def customer_name(self, obj):
        return obj.subscription.customer.user.username
    customer_name.short_description = 'Customer'

    def menu_name(self, obj):
        return obj.subscription.menu.name
    menu_name.short_description = 'Menu'
