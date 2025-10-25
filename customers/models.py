from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('regular', 'Энгийн үйлчлүүлэгч'),
        ('vip', 'VIP үйлчлүүлэгч'),
    ]
    
    first_name = models.CharField(max_length=100, verbose_name="Нэр")
    last_name = models.CharField(max_length=100, verbose_name="Овог")
    phone = models.CharField(max_length=20, verbose_name="Утасны дугаар")
    email = models.EmailField(blank=True, null=True, verbose_name="Имэйл")
    customer_type = models.CharField(
        max_length=10, 
        choices=CUSTOMER_TYPE_CHOICES, 
        default='regular',
        verbose_name="Үйлчлүүлэгчийн төрөл"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Бүртгэсэн огноо")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Сүүлд шинэчлэгдсэн огноо")
    
    class Meta:
        verbose_name = "Үйлчлүүлэгч"
        verbose_name_plural = "Үйлчлүүлэгчид"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"