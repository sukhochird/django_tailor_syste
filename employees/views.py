from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import models
from django.db.models import Avg, Count, Q
from .models import Employee
from .forms import EmployeeForm
from orders.models import Order, EmployeeRating


class SuperuserRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure only superusers can access"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.warning(request, 'Та энэ хуудсанд хандах эрхгүй байна.')
            return redirect('orders:order_list')
        return super().dispatch(request, *args, **kwargs)


class EmployeeListView(SuperuserRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Employee.objects.filter(is_active=True).order_by('last_name', 'first_name')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(last_name__icontains=search_query) |
                models.Q(first_name__icontains=search_query) |
                models.Q(phone__icontains=search_query)
            )
        
        # Employee type filter
        employee_type_filter = self.request.GET.get('employee_type')
        if employee_type_filter and employee_type_filter != 'all':
            queryset = queryset.filter(employee_type=employee_type_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employee_type_choices'] = Employee.EMPLOYEE_TYPE_CHOICES
        context['search_query'] = self.request.GET.get('search', '')
        context['employee_type_filter'] = self.request.GET.get('employee_type', 'all')
        
        # Summary statistics
        all_employees = Employee.objects.all()
        context['total_employees'] = all_employees.count()
        context['active_employees'] = all_employees.filter(is_active=True).count()
        context['inactive_employees'] = all_employees.filter(is_active=False).count()
        
        # Count by employee type
        context['summary_by_type'] = {}
        for emp_type, label in Employee.EMPLOYEE_TYPE_CHOICES:
            # Replace spaces with underscores for template access
            key = label.replace(' ', '_')
            context['summary_by_type'][key] = all_employees.filter(employee_type=emp_type).count()
        
        # Calculate total oёдолчин
        context['total_sewers'] = (
            context['summary_by_type'].get('Цамцны_эсгүүрчин', 0) +
            context['summary_by_type'].get('Пиджак_оёдолчин', 0) +
            context['summary_by_type'].get('Өмдний_оёдолчин', 0) +
            context['summary_by_type'].get('Цамцны_оёдолчин', 0)
        )
        
        return context


class EmployeeDetailView(SuperuserRequiredMixin, DetailView):
    model = Employee
    template_name = 'employees/employee_detail.html'
    context_object_name = 'employee'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_object()
        
        # Get all orders assigned to this employee
        assigned_orders = Order.objects.filter(
            Q(assigned_tailor=employee) | 
            Q(assigned_cutter=employee) | 
            Q(assigned_trouser_maker=employee)
        )
        
        # Order statistics
        context['total_orders'] = assigned_orders.count()
        context['completed_orders'] = assigned_orders.filter(current_status='seamstress_finished').count()
        context['in_progress_orders'] = assigned_orders.exclude(current_status='seamstress_finished').count()
        
        # Get employee ratings
        ratings = EmployeeRating.objects.filter(employee=employee)
        context['average_rating'] = ratings.aggregate(Avg('rating'))['rating__avg']
        context['total_ratings'] = ratings.count()
        
        # Recent orders - show last 20
        context['recent_orders'] = assigned_orders.order_by('-created_at')[:20]
        
        return context


class EmployeeCreateView(SuperuserRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Ажилтан амжилттай бүртгэгдлээ.')
        return super().form_valid(form)


class EmployeeUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Ажилтны мэдээлэл амжилттай шинэчлэгдлээ.')
        return super().form_valid(form)


class EmployeeDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Employee
    template_name = 'employees/employee_confirm_delete.html'
    success_url = reverse_lazy('employees:employee_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Ажилтан амжилттай устгагдлаа.')
        return super().delete(request, *args, **kwargs)