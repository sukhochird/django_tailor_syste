from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'customer_type', 'created_at']
    list_filter = ['customer_type', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Үндсэн мэдээлэл', {
            'fields': ('first_name', 'last_name', 'customer_type')
        }),
        ('Холбоо барих мэдээлэл', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Системийн мэдээлэл', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )