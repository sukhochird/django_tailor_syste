from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.db import models
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Report
from .forms import ReportForm
from orders.models import Order
from customers.models import Customer
from employees.models import Employee


class SuperuserRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure only superusers can access"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.warning(request, 'Та энэ хуудсанд хандах эрхгүй байна.')
            return redirect('orders:order_list')
        return super().dispatch(request, *args, **kwargs)


class ReportListView(SuperuserRequiredMixin, ListView):
    model = Report
    template_name = 'reports/report_list.html'
    context_object_name = 'reports'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Report.objects.all().order_by('-created_at')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query) |
                models.Q(description__icontains=search_query)
            )
        
        # Report type filter
        report_type_filter = self.request.GET.get('report_type')
        if report_type_filter and report_type_filter != 'all':
            queryset = queryset.filter(report_type=report_type_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameter
        period_filter = self.request.GET.get('period', 'this_month')
        
        # Get real statistics from database
        today = timezone.now().date()
        
        # Calculate date range based on filter
        if period_filter == 'this_month':
            start_date = today.replace(day=1)
            end_date = today
        elif period_filter == 'quarter':
            # Calculate quarter start (first day of current quarter)
            quarter = (today.month - 1) // 3
            start_date = today.replace(month=quarter * 3 + 1, day=1)
            end_date = today
        elif period_filter == 'this_year':
            start_date = today.replace(month=1, day=1)
            end_date = today
        elif period_filter == 'all_time':
            start_date = None
            end_date = today
        elif period_filter == 'custom':
            # Custom date range
            start_date_str = self.request.GET.get('start_date')
            end_date_str = self.request.GET.get('end_date')
            if start_date_str and end_date_str:
                from datetime import datetime
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            else:
                start_date = today.replace(day=1)
                end_date = today
        else:
            start_date = today.replace(day=1)
            end_date = today
        
        # Store filter info in context
        context['period_filter'] = period_filter
        context['start_date'] = start_date
        context['end_date'] = end_date
        
        # Previous period for comparison
        if start_date:
            prev_end_date = start_date - timedelta(days=1)
            if period_filter == 'this_month':
                if start_date.month == 1:
                    prev_start_date = start_date.replace(year=start_date.year - 1, month=12)
                else:
                    prev_start_date = start_date.replace(month=start_date.month - 1)
            elif period_filter == 'quarter':
                prev_start_date = start_date - timedelta(days=90)
            elif period_filter == 'this_year':
                prev_start_date = start_date.replace(year=start_date.year - 1)
            else:
                prev_start_date = None
        else:
            prev_start_date = None
            prev_end_date = None
        
        # Build base querysets with date filters
        current_period_orders = Order.objects.all()
        previous_period_orders = Order.objects.all()
        
        if start_date:
            # Use date lookup instead of datetime
            current_period_orders = current_period_orders.filter(created_at__date__gte=start_date)
            
            if prev_start_date:
                previous_period_orders = previous_period_orders.filter(
                    created_at__date__gte=prev_start_date,
                    created_at__date__lt=start_date
                )
            else:
                previous_period_orders = previous_period_orders.none()
        
        if end_date:
            current_period_orders = current_period_orders.filter(created_at__date__lte=end_date)
        
        # Total orders
        total_orders = current_period_orders.count()
        total_orders_previous = previous_period_orders.count()
        
        # Calculate percentage change
        if total_orders_previous > 0:
            order_change_percent = ((total_orders - total_orders_previous) / total_orders_previous * 100)
        else:
            order_change_percent = 0 if total_orders == 0 else 100
        
        # Total revenue - sum of all orders in the period (regardless of status)
        total_revenue = current_period_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        total_revenue_previous = previous_period_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        if total_revenue_previous > 0:
            revenue_change_percent = ((total_revenue - total_revenue_previous) / total_revenue_previous * 100)
        else:
            revenue_change_percent = 0 if total_revenue == 0 else 100
        
        # Completed orders
        completed_orders = current_period_orders.filter(current_status='seamstress_finished').count()
        completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
        
        # Overdue orders
        overdue_orders = current_period_orders.filter(
            due_date__lt=today
        ).exclude(current_status='seamstress_finished').count()
        
        # New customers
        new_customers_current = Customer.objects.all()
        new_customers_previous = Customer.objects.all()
        
        if start_date:
            new_customers_current = new_customers_current.filter(created_at__date__gte=start_date)
            if prev_start_date:
                new_customers_previous = new_customers_previous.filter(
                    created_at__date__gte=prev_start_date,
                    created_at__date__lt=start_date
                )
            else:
                new_customers_previous = new_customers_previous.none()
        
        if end_date:
            new_customers_current = new_customers_current.filter(created_at__date__lte=end_date)
        
        new_customers_this_month = new_customers_current.count()
        new_customers_last_month = new_customers_previous.count()
        
        if new_customers_last_month > 0:
            customers_change_percent = ((new_customers_this_month - new_customers_last_month) / new_customers_last_month * 100)
        else:
            customers_change_percent = 0 if new_customers_this_month == 0 else 100
        
        # Average completion time (in days)
        completed_orders_with_date = current_period_orders.filter(
            current_status='seamstress_finished',
            completed_date__isnull=False,
            start_date__isnull=False
        )
        
        avg_completion_days = None
        if completed_orders_with_date.exists():
            completion_times = []
            for order in completed_orders_with_date:
                if order.completed_date and order.start_date:
                    days = (order.completed_date - order.start_date).days
                    completion_times.append(days)
            
            if completion_times:
                avg_completion_days = sum(completion_times) / len(completion_times)
        
        # Employee performance
        employees_with_orders = Employee.objects.filter(is_active=True).annotate(
            completed_count=Count('tailor_orders', filter=Q(tailor_orders__current_status='seamstress_finished')) +
                           Count('cutter_orders', filter=Q(cutter_orders__current_status='seamstress_finished')) +
                           Count('trouser_maker_orders', filter=Q(trouser_maker_orders__current_status='seamstress_finished'))
        ).filter(completed_count__gt=0).order_by('-completed_count')[:3]
        
        # Material statistics
        unique_materials = Order.objects.exclude(
            material_code__isnull=True
        ).exclude(material_code='').values('material_code').distinct().count()
        
        low_usage_materials = Order.objects.exclude(
            material_code__isnull=True
        ).exclude(material_code='').values('material_code').annotate(
            count=Count('id')
        ).filter(count__lt=2).count()
        
        # Add to context
        context['report_type_choices'] = Report.REPORT_TYPE_CHOICES
        context['search_query'] = self.request.GET.get('search', '')
        context['report_type_filter'] = self.request.GET.get('report_type', 'all')
        
        # Summary statistics
        context['total_orders'] = total_orders
        context['order_change_percent'] = order_change_percent
        
        context['total_revenue'] = total_revenue
        context['revenue_change_percent'] = revenue_change_percent
        
        context['completed_orders'] = completed_orders
        context['completion_rate'] = completion_rate
        
        context['overdue_orders'] = overdue_orders
        
        context['new_customers_this_month'] = new_customers_this_month
        context['customers_change_percent'] = customers_change_percent
        
        context['avg_completion_days'] = int(avg_completion_days) if avg_completion_days else None
        
        context['top_employees'] = employees_with_orders
        
        context['unique_materials'] = unique_materials
        context['low_usage_materials'] = low_usage_materials
        
        return context


class ReportDetailView(SuperuserRequiredMixin, DetailView):
    model = Report
    template_name = 'reports/report_detail.html'
    context_object_name = 'report'


class ReportCreateView(SuperuserRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = 'reports/report_form.html'
    success_url = reverse_lazy('reports:report_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Тайлан амжилттай үүсгэгдлээ.')
        return super().form_valid(form)


class ReportDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Report
    template_name = 'reports/report_confirm_delete.html'
    success_url = reverse_lazy('reports:report_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Тайлан амжилттай устгагдлаа.')
        return super().delete(request, *args, **kwargs)