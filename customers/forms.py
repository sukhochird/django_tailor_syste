from django import forms
from .models import Customer


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'first_name', 'last_name', 'phone', 'email', 
            'customer_type'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Жишээ: Болд'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Жишээ: Батбаяр'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'placeholder': 'Жишээ: 99112233'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Жишээ: bold@email.com'}),
            'customer_type': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Нэр *',
            'last_name': 'Овог *',
            'phone': 'Утасны дугаар *',
            'email': 'Имэйл',
            'customer_type': 'Үйлчлүүлэгчийн төрөл',
        }
        help_texts = {
            'first_name': 'Үйлчлүүлэгчийн нэрийг оруулна уу',
            'last_name': 'Үйлчлүүлэгчийн овгийг оруулна уу',
            'phone': '8 оронтой утасны дугаар оруулна уу (жишээ: 99112233)',
            'email': 'Имэйл сонголттой бөгөөд шаардлагагүй',
            'customer_type': 'Үйлчлүүлэгчийн төрөлийг сонгоно уу',
        }
