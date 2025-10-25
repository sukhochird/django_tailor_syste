from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import secrets
import string


class Employee(models.Model):
    EMPLOYEE_TYPE_CHOICES = [
        ('manager', 'Менежер'),
        ('cutter', 'Эсгүүрчин'),
        ('shirt_cutter', 'Цамцны эсгүүрчин'),
        ('jacket_sewer', 'Пиджак оёдолчин'),
        ('trouser_sewer', 'Өмдний оёдолчин'),
        ('shirt_sewer', 'Цамцны оёдолчин'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Хэрэглэгч")
    last_name = models.CharField(max_length=100, verbose_name="Овог", default='')
    first_name = models.CharField(max_length=100, verbose_name="Нэр", default='')
    phone = models.CharField(max_length=20, verbose_name="Утасны дугаар", default='')
    employee_type = models.CharField(
        max_length=20,
        choices=EMPLOYEE_TYPE_CHOICES,
        verbose_name="Албан тушаал"
    )
    is_active = models.BooleanField(default=True, verbose_name="Идэвхтэй")
    has_login_access = models.BooleanField(default=False, verbose_name="Нэвтрэх эрхтэй")
    login_password = models.CharField(max_length=128, blank=True, null=True, verbose_name="Нууц үг", help_text="Хэрэв хоосон байвал автоматаар үүснэ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Бүртгэсэн огноо")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Сүүлд шинэчлэгдсэн огноо")
    
    class Meta:
        verbose_name = "Ажилтан"
        verbose_name_plural = "Ажилтнууд"
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.get_employee_type_display()})"
    
    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"
    
    def generate_password(self, length=8):
        """Generate a random secure password"""
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        return password
    
    def create_user_account(self):
        """Create Django User account for this employee"""
        if not self.user and self.has_login_access:
            username = self.phone  # Use phone as username
            
            # Use custom password if set, otherwise generate one
            if self.login_password:
                password = self.login_password
            else:
                password = self.generate_password()
                self.login_password = password
                self.save()
            
            user = User.objects.create_user(
                username=username,
                first_name=self.first_name,
                last_name=self.last_name,
                password=password
            )
            self.user = user
            self.save()
            return user
        return None
    
    def reset_password(self, new_password=None):
        """Reset password for the user account"""
        if self.user:
            if new_password is None:
                new_password = self.generate_password()
            
            self.user.set_password(new_password)
            self.user.save()
            self.login_password = new_password
            self.save()
            return new_password
        return None
    
    def delete_user_account(self):
        """Delete Django User account for this employee"""
        if self.user:
            user = self.user
            self.user = None
            self.save()
            user.delete()
            return True
        return False


@receiver(post_save, sender=Employee)
def update_user_account(sender, instance, created, **kwargs):
    """Automatically create user account when employee is saved"""
    if instance.has_login_access:
        if not instance.user:
            # Create user account if login access is enabled and no user is manually selected
            instance.create_user_account()
        # Note: If user is manually selected, don't auto-update it
    else:
        # Remove user account if login access is disabled
        if instance.user:
            instance.delete_user_account()


@receiver(pre_delete, sender=Employee)
def delete_user_on_employee_delete(sender, instance, **kwargs):
    """Delete associated user account when employee is deleted"""
    if instance.user:
        instance.user.delete()
        