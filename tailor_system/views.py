from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from orders.models import Order
from customers.models import Customer
from employees.models import Employee


def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Сайн байна уу, {user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Нэвтрэх нэр эсвэл нууц үг буруу байна.')
    
    return render(request, 'login.html')


def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.success(request, 'Амжилттай гарлаа.')
    return redirect('login')


@login_required
def dashboard(request):
    """Dashboard view showing system overview"""
    # Only superusers can access dashboard
    if not request.user.is_superuser:
        messages.warning(request, 'Та энэ хуудсанд хандах эрхгүй байна.')
        return redirect('orders:order_list')
    
    from django.db.models import Sum, Count, Case, When, BooleanField
    from django.utils import timezone
    from datetime import timedelta
    from decimal import Decimal
    
    # Get recent orders with overdue first
    recent_orders = Order.objects.select_related('customer').order_by('-created_at')[:12]
    
    # Sort in Python to prioritize overdue orders
    recent_orders = list(recent_orders)
    recent_orders.sort(key=lambda x: (not x.is_overdue, x.created_at), reverse=True)
    
    # Get statistics
    total_orders = Order.objects.count()
    active_orders = Order.objects.exclude(current_status='seamstress_finished').count()
    completed_orders = Order.objects.filter(current_status='seamstress_finished').count()
    pending_orders = Order.objects.filter(current_status='order_placed').count()
    
    # Get overdue orders
    today = timezone.now().date()
    overdue_orders = Order.objects.filter(
        due_date__lt=today
    ).exclude(current_status='seamstress_finished').count()
    
    # Calculate revenue
    # Total revenue from completed orders
    total_revenue = Order.objects.filter(
        current_status='seamstress_finished'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    # Current month revenue
    month_start = today.replace(day=1)
    current_month_revenue = Order.objects.filter(
        current_status='seamstress_finished',
        completed_date__gte=month_start
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    # Previous month revenue for comparison
    if month_start.month == 1:
        prev_month_start = month_start.replace(year=month_start.year - 1, month=12)
    else:
        prev_month_start = month_start.replace(month=month_start.month - 1)
    
    prev_month_revenue = Order.objects.filter(
        current_status='seamstress_finished',
        completed_date__gte=prev_month_start,
        completed_date__lt=month_start
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    
    # Calculate percentage change
    if prev_month_revenue > 0:
        revenue_change_percent = ((current_month_revenue - prev_month_revenue) / prev_month_revenue * 100)
    else:
        revenue_change_percent = 0 if current_month_revenue == 0 else 100
    
    # Get other statistics
    total_customers = Customer.objects.count()
    
    # Count active customers (customers with at least one order in last 3 months)
    three_months_ago = today - timedelta(days=90)
    active_customers = Customer.objects.filter(
        order__created_at__gte=three_months_ago
    ).distinct().count()
    
    # New customers this month
    new_customers_this_month = Customer.objects.filter(
        created_at__gte=month_start
    ).count()
    
    total_employees = Employee.objects.filter(is_active=True).count()
    
    # Count unique material codes from orders
    total_materials = Order.objects.exclude(
        material_code__isnull=True
    ).exclude(material_code='').values('material_code').distinct().count()
    
    # Materials with low usage (used in less than 2 orders)
    low_stock_materials = Order.objects.exclude(
        material_code__isnull=True
    ).exclude(material_code='').values('material_code').annotate(
        count=Count('id')
    ).filter(count__lt=2).count()
    
    # Calculate order stats changes (last 3 months)
    three_months_ago = today - timedelta(days=90)
    orders_last_3_months = Order.objects.filter(
        created_at__gte=three_months_ago
    ).count()
    
    # Calculate percentage changes for display
    total_change_percent = 8  # Hardcoded for now, can be calculated from historical data
    completed_change_percent = 14  # Hardcoded for now
    
    context = {
        'recent_orders': recent_orders,
        'total_orders': total_orders,
        'active_orders': active_orders,
        'completed_orders': completed_orders,
        'pending_orders': pending_orders,
        'overdue_orders': overdue_orders,
        'total_customers': total_customers,
        'active_customers': active_customers,
        'new_customers_this_month': new_customers_this_month,
        'total_employees': total_employees,
        'total_materials': total_materials,
        'low_stock_materials': low_stock_materials,
        'total_revenue': total_revenue,
        'current_month_revenue': current_month_revenue,
        'revenue_change_percent': revenue_change_percent,
        'total_change_percent': total_change_percent,
        'completed_change_percent': completed_change_percent,
    }
    
    return render(request, 'dashboard.html', context)
