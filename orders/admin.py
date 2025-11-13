from decimal import Decimal

from django.contrib import admin
from .models import Order, ProcessStep, OrderRating, EmployeeRating, OrderStatusHistory


class ProcessStepInline(admin.TabularInline):
    model = ProcessStep
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['completed_at']
    can_delete = False


class EmployeeRatingInline(admin.TabularInline):
    model = EmployeeRating
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'item_type', 'current_status', 'total_amount', 'advance_amount', 'remaining_amount_display', 'due_date', 'is_overdue', 'days_remaining_display', 'created_at']
    list_filter = ['current_status', 'item_type', 'customer__customer_type', 'created_at', 'due_date']
    search_fields = ['order_number', 'customer__first_name', 'customer__last_name', 'item_type', 'material_code']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'order_number']
    inlines = [ProcessStepInline, OrderStatusHistoryInline, EmployeeRatingInline]
    
    fieldsets = (
        ('Үндсэн мэдээлэл', {
            'fields': ('order_number', 'customer', 'item_type', 'current_status')
        }),
        ('Материал', {
            'fields': ('material_code',)
        }),
        ('Ажилтнууд', {
            'fields': ('assigned_tailor', 'assigned_cutter', 'assigned_trouser_maker'),
            'classes': ('collapse',)
        }),
        ('Үнэ', {
            'fields': ('total_amount', 'advance_amount'),
            'classes': ('collapse',)
        }),
        ('Огноо', {
            'fields': ('start_date', 'due_date', 'completed_date')
        }),
        ('Нэмэлт', {
            'fields': ('notes', 'is_rated'),
            'classes': ('collapse',)
        }),
        ('Системийн мэдээлэл', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Хугацаа хэтэрсэн'
    
    def days_remaining_display(self, obj):
        days = obj.days_remaining
        if days > 0:
            return f"{days} хоног үлдсэн"
        elif days == 0:
            return "Өнөөдөр"
        else:
            return f"{abs(days)} хоног хэтэрсэн"
    days_remaining_display.short_description = 'Үлдсэн хугацаа'
    
    def remaining_amount_display(self, obj):
        remaining = obj.remaining_amount
        if remaining == Decimal('0'):
            return "Бүрэн төлсөн"
        return f"{remaining:,.0f}₮"
    remaining_amount_display.short_description = 'Үлдэгдэл'


@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ['order', 'title', 'status', 'completed_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'title', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(OrderRating)
class OrderRatingAdmin(admin.ModelAdmin):
    list_display = ['order', 'overall_rating', 'quality_rating', 'service_rating', 'timing_rating', 'created_at']
    list_filter = ['overall_rating', 'created_at']
    search_fields = ['order__order_number', 'comments']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'completed_by', 'completed_at']
    list_filter = ['status', 'completed_at']
    search_fields = ['order__order_number', 'completed_by__first_name', 'completed_by__last_name', 'notes']
    ordering = ['-completed_at']
    readonly_fields = ['completed_at']
    
    fieldsets = (
        ('Үндсэн мэдээлэл', {
            'fields': ('order', 'status')
        }),
        ('Дуусгасан мэдээлэл', {
            'fields': ('completed_by', 'completed_at', 'notes')
        }),
    )


@admin.register(EmployeeRating)
class EmployeeRatingAdmin(admin.ModelAdmin):
    list_display = ['order', 'employee', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['order__order_number', 'employee__first_name', 'employee__last_name', 'comment']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Үндсэн мэдээлэл', {
            'fields': ('order', 'employee', 'rating')
        }),
        ('Сэтгэгдэл', {
            'fields': ('comment',)
        }),
        ('Системийн мэдээлэл', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )