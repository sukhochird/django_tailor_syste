from django.contrib import admin
from django.contrib import messages
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'employee_type', 'phone', 'is_active', 'has_login_access', 'created_at']
    list_filter = ['employee_type', 'is_active', 'has_login_access', 'created_at']
    search_fields = ['last_name', 'first_name', 'phone']
    ordering = ['last_name', 'first_name']
    readonly_fields = ['created_at', 'updated_at', 'user', 'get_password']
    actions = ['reset_passwords']
    
    fieldsets = (
        ('Үндсэн мэдээлэл', {
            'fields': ('last_name', 'first_name', 'employee_type', 'phone')
        }),
        ('Нэвтрэх эрх', {
            'fields': ('has_login_access', 'user', 'login_password', 'get_password'),
            'description': 'Хэрэв "Нэвтрэх эрхтэй" гэсэн талбарыг сонговол автоматаар Django хэрэглэгч үүснэ. Нууц үг хоосон байвал автоматаар үүснэ.'
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
        ('Системийн мэдээлэл', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_password(self, obj):
        """Display password if it exists"""
        if obj.login_password:
            return f"•••••••• ({obj.login_password[:3]}...)"
        return "Автоматаар үүснэ"
    get_password.short_description = 'Одоогийн нууц үг'
    
    def reset_passwords(self, request, queryset):
        """Reset passwords for selected employees"""
        count = 0
        for employee in queryset:
            if employee.has_login_access and employee.user:
                new_password = employee.reset_password()
                if new_password:
                    count += 1
                    self.message_user(
                        request,
                        f'{employee.full_name}: Шинэ нууц үг - {new_password}',
                        messages.INFO
                    )
        
        if count > 0:
            self.message_user(
                request,
                f'{count} ажилтны нууц үг амжилттай шинэчлэгдлээ.',
                messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                'Сонгосон ажилтнуудын нууц үг шинэчлэх боломжгүй.',
                messages.WARNING
            )
    reset_passwords.short_description = 'Сонгосон ажилтнуудын нууц үг шинэчлэх'