from django.db import models


class Material(models.Model):
    name = models.CharField(max_length=100, verbose_name="Материалын нэр")
    description = models.TextField(blank=True, null=True, verbose_name="Тайлбар")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Нэгжийн үнэ")
    unit = models.CharField(max_length=20, default="метр", verbose_name="Хэмжих нэгж")
    stock_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Үлдэгдэл")
    supplier = models.CharField(max_length=100, blank=True, null=True, verbose_name="Нийлүүлэгч")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Бүртгэсэн огноо")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Сүүлд шинэчлэгдсэн огноо")
    
    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалууд"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.unit_price}₮/{self.unit})"
    
    @property
    def is_low_stock(self):
        return self.stock_quantity < 10  # 10-аас бага бол бага гэж үзнэ
    
    @property
    def total_value(self):
        return self.stock_quantity * self.unit_price