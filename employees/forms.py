from django import forms
from .models import Employee
import re


class EmployeeForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ажилтны нэрийг оруулна уу',
            'required': True
        }),
        label='Нэр',
        help_text='Ажилтны нэрийг оруулна уу'
    )
    
    last_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ажилтны овгийг оруулна уу'
        }),
        label='Овог',
        help_text='Ажилтны овгийг оруулна уу (сонголттой)'
    )
    
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '99123456',
            'required': True,
            'pattern': '[0-9]{8,12}',
            'title': '8-12 оронтой тоо оруулна уу'
        }),
        label='Утасны дугаар',
        help_text='Утасны дугаарыг оруулна уу (99123456)'
    )
    
    employee_type = forms.ChoiceField(
        choices=Employee.EMPLOYEE_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'required': True
        }),
        label='Албан тушаал',
        help_text='Ажилтны албан тушаалыг сонгоно уу'
    )
    
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Идэвхтэй',
        help_text='Энэ ажилтан идэвхтэй эсэх'
    )
    
    has_login_access = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Нэвтрэх эрхтэй',
        help_text='Энэ ажилтан системд нэвтрэх эрхтэй эсэх'
    )
    
    login_password = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Хоосон байвал автоматаар үүснэ',
            'type': 'text'
        }),
        label='Нууц үг',
        help_text='Нууц үг тохируулах (хоосон байвал автоматаар үүснэ)'
    )
    
    class Meta:
        model = Employee
        fields = [
            'last_name', 'first_name', 'phone', 'employee_type', 'is_active', 'has_login_access', 'login_password'
        ]
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name or len(first_name.strip()) == 0:
            raise forms.ValidationError('Ажилтны нэрийг оруулах шаардлагатай.')
        if len(first_name) < 2:
            raise forms.ValidationError('Нэр хэт богино байна. Хамгийн багадаа 2 тэмдэгт байх ёстой.')
        return first_name.strip()
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError('Утасны дугаар оруулах шаардлагатай.')
        
        # Зөвхөн тоо байгаа эсэхийг шалгах
        if not re.match(r'^[0-9]+$', phone):
            raise forms.ValidationError('Утасны дугаар нь зөвхөн тооноос бүрдэх ёстой.')
        
        # Утасны дугаарын уртыг шалгах
        if len(phone) < 8 or len(phone) > 12:
            raise forms.ValidationError('Утасны дугаар 8-12 оронтой байх ёстой.')
        
        # Өмнө нь орсон эсэхийг шалгах
        existing = Employee.objects.filter(phone=phone)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError('Энэ утасны дугаар аль хэдийн бүртгэгдсэн байна.')
        
        return phone
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            return last_name.strip()
        return ''
    
    def save(self, commit=True):
        """Save the employee instance"""
        employee = super().save(commit=False)
        
        if commit:
            employee.save()
        
        return employee
