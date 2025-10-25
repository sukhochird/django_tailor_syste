from django.contrib import admin
from .models import Report, SystemSettings


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'description', 'updated_at']
    search_fields = ['key', 'value', 'description']
    ordering = ['key']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('Үндсэн мэдээлэл', {
            'fields': ('key', 'value', 'description')
        }),
        ('Системийн мэдээлэл', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'created_by', 'period_start', 'period_end', 'created_at']
    list_filter = ['report_type', 'created_at', 'period_start', 'period_end']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Үндсэн мэдээлэл', {
            'fields': ('title', 'report_type', 'description')
        }),
        ('Хугацаа', {
            'fields': ('period_start', 'period_end')
        }),
        ('Тайлангийн өгөгдөл', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Системийн мэдээлэл', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )