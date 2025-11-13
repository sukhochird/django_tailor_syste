from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.db import models
from django.db.models import Count, Sum, Avg, Q, F, Case, When, Value, ExpressionWrapper
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
        
        # Get filter parameter - default to all time to ensure data visibility
        period_filter = self.request.GET.get('period', 'all_time')
        
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
            end_date = None
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
        previous_period_orders = Order.objects.none()
        
        if start_date:
            # Use date lookup instead of datetime
            current_period_orders = current_period_orders.filter(created_at__date__gte=start_date)
            
            if prev_start_date:
                previous_period_orders = Order.objects.filter(
                    created_at__date__gte=prev_start_date,
                    created_at__date__lt=start_date
                )
        
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
        
        # Revenue calculations
        decimal_output = models.DecimalField(max_digits=12, decimal_places=2)
        
        collected_expression = Case(
            When(advance_amount__gt=0, then=F('advance_amount')),
            default=F('total_amount'),
            output_field=decimal_output
        )
        
        outstanding_expression = Case(
            When(
                advance_amount__gt=0,
                then=ExpressionWrapper(
                    F('total_amount') - F('advance_amount'),
                    output_field=decimal_output
                )
            ),
            default=Value(0),
            output_field=decimal_output
        )
        
        total_revenue = current_period_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        total_revenue_previous = previous_period_orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        
        collected_revenue = current_period_orders.aggregate(total=Sum(collected_expression))['total'] or Decimal('0')
        collected_revenue_previous = previous_period_orders.aggregate(total=Sum(collected_expression))['total'] or Decimal('0')
        
        outstanding_revenue = current_period_orders.aggregate(total=Sum(outstanding_expression))['total'] or Decimal('0')
        
        if total_revenue_previous > 0:
            revenue_change_percent = ((total_revenue - total_revenue_previous) / total_revenue_previous * 100)
        else:
            revenue_change_percent = 0 if total_revenue == 0 else 100
        
        if collected_revenue_previous > 0:
            collected_change_percent = ((collected_revenue - collected_revenue_previous) / collected_revenue_previous * 100)
        else:
            collected_change_percent = 0 if collected_revenue == 0 else 100
        
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
        
        # Province statistics
        province_stats = []
        for province_code, province_name in Customer.PROVINCE_CHOICES:
            province_customers = Customer.objects.filter(province=province_code)
            if start_date:
                province_customers = province_customers.filter(created_at__date__gte=start_date)
            if end_date:
                province_customers = province_customers.filter(created_at__date__lte=end_date)
            
            customer_count = province_customers.count()
            
            # Get orders from these customers
            province_orders = Order.objects.filter(
                customer__province=province_code
            )
            if start_date:
                province_orders = province_orders.filter(created_at__date__gte=start_date)
            if end_date:
                province_orders = province_orders.filter(created_at__date__lte=end_date)
            
            order_count = province_orders.count()
            province_totals = province_orders.aggregate(
                total=Sum('total_amount'),
                collected=Sum(collected_expression),
                outstanding=Sum(outstanding_expression)
            )
            province_revenue = province_totals.get('total') or Decimal('0')
            province_collected = province_totals.get('collected') or Decimal('0')
            province_outstanding = province_totals.get('outstanding') or Decimal('0')
            
            if customer_count > 0 or order_count > 0:
                province_stats.append({
                    'name': province_name,
                    'code': province_code,
                    'customers': customer_count,
                    'orders': order_count,
                    'revenue': province_revenue,
                    'collected': province_collected,
                    'outstanding': province_outstanding
                })
        
        # Sort by customers count descending
        province_stats.sort(key=lambda x: x['customers'], reverse=True)
        
        # Add to context
        context['report_type_choices'] = Report.REPORT_TYPE_CHOICES
        context['search_query'] = self.request.GET.get('search', '')
        context['report_type_filter'] = self.request.GET.get('report_type', 'all')
        
        # Summary statistics
        context['total_orders'] = total_orders
        context['order_change_percent'] = order_change_percent
        
        context['total_revenue'] = total_revenue
        context['revenue_change_percent'] = revenue_change_percent
        context['collected_revenue'] = collected_revenue
        context['collected_change_percent'] = collected_change_percent
        context['outstanding_revenue'] = outstanding_revenue
        
        context['completed_orders'] = completed_orders
        context['completion_rate'] = completion_rate
        
        context['overdue_orders'] = overdue_orders
        
        context['new_customers_this_month'] = new_customers_this_month
        context['customers_change_percent'] = customers_change_percent
        
        context['avg_completion_days'] = int(avg_completion_days) if avg_completion_days else None
        
        context['top_employees'] = employees_with_orders
        
        context['unique_materials'] = unique_materials
        context['low_usage_materials'] = low_usage_materials
        
        context['province_stats'] = province_stats
        
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


@login_required
def show_employee_workload(request):
    """Show employee workload report"""
    if not request.user.is_superuser:
        messages.warning(request, 'Та энэ хуудсанд хандах эрхгүй байна.')
        return redirect('orders:order_list')
    
    employees = Employee.objects.filter(is_active=True).order_by('last_name', 'first_name')
    
    # Calculate workload for each employee
    employee_data = []
    for employee in employees:
        # Get all orders assigned to this employee (as tailor, cutter, or trouser maker)
        tailor_orders = employee.tailor_orders.exclude(current_status='seamstress_finished')
        cutter_orders = employee.cutter_orders.exclude(current_status='seamstress_finished')
        trouser_maker_orders = employee.trouser_maker_orders.exclude(current_status='seamstress_finished')
        
        # Total active orders
        total_active = tailor_orders.count() + cutter_orders.count() + trouser_maker_orders.count()
        
        # Completed orders
        completed_tailor = employee.tailor_orders.filter(current_status='seamstress_finished').count()
        completed_cutter = employee.cutter_orders.filter(current_status='seamstress_finished').count()
        completed_trouser = employee.trouser_maker_orders.filter(current_status='seamstress_finished').count()
        total_completed = completed_tailor + completed_cutter + completed_trouser
        
        # Overdue orders
        today = timezone.now().date()
        overdue_tailor = tailor_orders.filter(due_date__lt=today).count()
        overdue_cutter = cutter_orders.filter(due_date__lt=today).count()
        overdue_trouser = trouser_maker_orders.filter(due_date__lt=today).count()
        total_overdue = overdue_tailor + overdue_cutter + overdue_trouser
        
        # Calculate workload indicator
        if total_active == 0:
            workload_status = 'low'
            workload_text = 'Хоосон'
        elif total_active <= 3:
            workload_status = 'normal'
            workload_text = 'Хэвийн'
        elif total_active <= 6:
            workload_status = 'high'
            workload_text = 'Өндөр'
        else:
            workload_status = 'critical'
            workload_text = 'Маш өндөр'
        
        employee_data.append({
            'employee': employee,
            'total_active': total_active,
            'total_completed': total_completed,
            'total_overdue': total_overdue,
            'workload_status': workload_status,
            'workload_text': workload_text,
            'tailor_orders': tailor_orders.count(),
            'cutter_orders': cutter_orders.count(),
            'trouser_maker_orders': trouser_maker_orders.count(),
        })
    
    # Sort by total active orders (descending)
    employee_data.sort(key=lambda x: x['total_active'], reverse=True)
    
    # Calculate totals
    total_active_orders = sum(emp['total_active'] for emp in employee_data)
    total_overdue_orders = sum(emp['total_overdue'] for emp in employee_data)
    total_completed_orders = sum(emp['total_completed'] for emp in employee_data)
    
    context = {
        'employee_data': employee_data,
        'total_employees': len(employee_data),
        'total_active_orders': total_active_orders,
        'total_overdue_orders': total_overdue_orders,
        'total_completed_orders': total_completed_orders,
    }
    
    return render(request, 'reports/employee_workload.html', context)