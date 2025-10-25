from django import forms
from .models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            'title', 'report_type', 'description', 
            'period_start', 'period_end'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'report_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'period_start': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'period_end': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
