from django.contrib import admin
from .models import Material


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit_price', 'stock_quantity', 'supplier', 'is_low_stock', 'created_at']
    list_filter = ['supplier', 'created_at']
    search_fields = ['name', 'description', 'supplier']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Үндсэн мэдээлэл', {
            'fields': ('name', 'description')
        }),
        ('Үнэ болон нөөц', {
            'fields': ('unit_price', 'unit', 'stock_quantity')
        }),
        ('Нийлүүлэгч', {
            'fields': ('supplier',)
        }),
        ('Системийн мэдээлэл', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Бага нөөц'