from django.db import models
from django.contrib.auth.models import User


class SystemSettings(models.Model):
    """System-wide settings"""
    key = models.CharField(max_length=100, unique=True, verbose_name="Түлхүүр")
    value = models.CharField(max_length=500, verbose_name="Утга")
    description = models.TextField(blank=True, null=True, verbose_name="Тайлбар")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Сүүлд шинэчлэгдсэн огноо")
    
    class Meta:
        verbose_name = "Системийн тохиргоо"
        verbose_name_plural = "Системийн тохиргоонууд"
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key}: {self.value}"
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Get a setting value by key"""
        try:
            return cls.objects.get(key=key).value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_setting(cls, key, value, description=None):
        """Set a setting value"""
        setting, created = cls.objects.get_or_create(key=key)
        setting.value = value
        if description:
            setting.description = description
        setting.save()
        return setting


class Report(models.Model):
    REPORT_TYPE_CHOICES = [
        ('orders_summary', 'Захиалгын хураангуй'),
        ('employee_performance', 'Ажилтны гүйцэтгэл'),
        ('customer_analysis', 'Үйлчлүүлэгчийн шинжилгээ'),
        ('material_usage', 'Материалын хэрэглээ'),
        ('financial_summary', 'Санхүүгийн хураангуй'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Тайлангийн гарчиг")
    report_type = models.CharField(
        max_length=50,
        choices=REPORT_TYPE_CHOICES,
        verbose_name="Тайлангийн төрөл"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Тайлбар")
    data = models.JSONField(default=dict, verbose_name="Тайлангийн өгөгдөл")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Үүсгэсэн хүн")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Үүсгэсэн огноо")
    period_start = models.DateField(verbose_name="Хугацааны эхлэл")
    period_end = models.DateField(verbose_name="Хугацааны төгсгөл")
    
    class Meta:
        verbose_name = "Тайлан"
        verbose_name_plural = "Тайлангууд"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.period_start} - {self.period_end})"