
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
import uuid
from .models import *

@admin.register(HomeContent)
class HomeContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'priority', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle')
    ordering = ('-priority', '-created_at')

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

from import_export import resources, fields
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.models import User

class CustomerProfileResource(resources.ModelResource):
    username = fields.Field(attribute='user', column_name='username')
    zone_name = fields.Field(attribute='zone', column_name='zone')
    route_name = fields.Field(attribute='route', column_name='route')

    class Meta:
        model = CustomerProfile
        fields = ('username', 'phone', 'zone_name', 'route_name', 'building_name', 'floor_number', 'flat_number')
        import_id_fields = ('username',)

    def before_import_row(self, row, **kwargs):
        username = row.get('username')
        # Create user if doesn't exist
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(username=username, password='temp123')

    def get_instance(self, instance_loader, row):
        try:
            params = {}
            for key in instance_loader.resource.get_import_id_fields():
                field = instance_loader.resource.fields[key]
                params[field.attribute] = field.clean(row)
            if params:
                return User.objects.get(username=params['user'])
        except User.DoesNotExist:
            return None

@admin.register(CustomerProfile)
class CustomerProfileAdmin(ImportExportModelAdmin):
    resource_class = CustomerProfileResource
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
    list_display = ('customer', 'menu', 'start_date', 'end_date', 'payment_mode', 'status', 'get_selected_days', 'get_delivery_stats')
    list_filter = ('payment_mode', 'time_slot', 'start_date', 'end_date', 'status')
    actions = ['approve_subscriptions', 'reject_subscriptions']

    def approve_subscriptions(self, request, queryset):
        queryset.update(status='approved')
    approve_subscriptions.short_description = "Approve selected subscriptions"

    def reject_subscriptions(self, request, queryset):
        queryset.update(status='rejected')
    reject_subscriptions.short_description = "Reject selected subscriptions"
    search_fields = ('customer__user__username', 'menu__name')

    def get_selected_days(self, obj):
        days = {
            '0': 'Mon', '1': 'Tue', '2': 'Wed',
            '3': 'Thu', '4': 'Fri', '5': 'Sat', '6': 'Sun'
        }
        selected = [days[day] for day in obj.selected_days]
        return ', '.join(selected)
    get_selected_days.short_description = 'Delivery Days'
    
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


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'amount', 'transaction_type', 'description', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('customer__user__username', 'reference_id', 'description')
    readonly_fields = ('created_at', 'reference_id')

    def save_model(self, request, obj, form, change):
        if not obj.reference_id:
            obj.reference_id = str(uuid.uuid4())
        
        if not change:  # Only update balance on new transactions
            if obj.transaction_type == 'credit':
                obj.customer.wallet_balance += obj.amount
            else:
                obj.customer.wallet_balance -= obj.amount
            obj.customer.save()
            
        super().save_model(request, obj, form, change)
