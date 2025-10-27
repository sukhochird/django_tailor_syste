from django import forms
from django.contrib.auth.models import User
from .models import Order, ProcessStep, EmployeeRating
from customers.models import Customer
from employees.models import Employee


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'customer', 'item_type', 'material_code',
            'assigned_tailor', 'assigned_cutter', 'assigned_trouser_maker',
            'total_amount', 'start_date', 'due_date', 'notes',
            'design_front', 'design_back', 'design_side', 'design_reference'
        ]
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'material_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Материалын код'}),
            'assigned_tailor': forms.Select(attrs={'class': 'form-control'}),
            'assigned_cutter': forms.Select(attrs={'class': 'form-control'}),
            'assigned_trouser_maker': forms.Select(attrs={'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'design_front': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'design_back': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'design_side': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'design_reference': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Allow selecting from all active employees, ordered alphabetically
        all_employees = Employee.objects.filter(is_active=True).order_by('last_name', 'first_name')
        
        self.fields['assigned_cutter'].queryset = all_employees
        self.fields['assigned_tailor'].queryset = all_employees
        self.fields['assigned_trouser_maker'].queryset = all_employees
        
        # Set default dates
        from datetime import date, timedelta
        from reports.models import SystemSettings
        
        if not self.instance.pk:  # Only for new orders
            # Default start date to today
            self.fields['start_date'].initial = date.today()
            
            # Default due date from settings or 14 days
            days_to_complete = SystemSettings.get_setting('default_order_duration', '14')
            try:
                days = int(days_to_complete)
            except ValueError:
                days = 14
            self.fields['due_date'].initial = date.today() + timedelta(days=days)
            
            # Default total amount from settings
            default_amount = SystemSettings.get_setting('default_order_amount', '100000')
            try:
                self.fields['total_amount'].initial = float(default_amount)
            except ValueError:
                self.fields['total_amount'].initial = 100000


class ProcessStepForm(forms.ModelForm):
    class Meta:
        model = ProcessStep
        fields = ['step_type', 'title', 'description', 'status']
        widgets = {
            'step_type': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class EmployeeRatingForm(forms.ModelForm):
    class Meta:
        model = EmployeeRating
        fields = ['employee', 'rating', 'comment']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5, 'step': 1}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
