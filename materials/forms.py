from django import forms
from .models import Material


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = [
            'name', 'description', 'unit_price', 'unit', 
            'stock_quantity', 'supplier'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
        }
