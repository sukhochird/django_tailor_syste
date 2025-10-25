from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
from .models import Order, ProcessStep, OrderRating, OrderStatusHistory, EmployeeRating
from .forms import OrderForm, ProcessStepForm, EmployeeRatingForm
from customers.models import Customer
from employees.models import Employee


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Order.objects.select_related('customer')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(order_number__icontains=search_query) |
                models.Q(customer__first_name__icontains=search_query) |
                models.Q(customer__last_name__icontains=search_query)
            )
        
        # Status filter
        status_filter = self.request.GET.get('status')
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(current_status=status_filter)
        
        # Item type filter
        item_type_filter = self.request.GET.get('item_type')
        if item_type_filter and item_type_filter != 'all':
            queryset = queryset.filter(item_type=item_type_filter)
        
        # Sort: overdue first, then by creation date
        # We'll sort in Python since we need to use the model property
        orders = list(queryset.order_by('-created_at'))
        orders.sort(key=lambda x: (not x.is_overdue, x.created_at), reverse=True)
        
        return orders
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all orders for statistics
        all_orders = Order.objects.all()
        
        # Calculate statistics
        context['total_orders'] = all_orders.count()
        context['active_orders'] = all_orders.exclude(current_status='seamstress_finished').count()
        context['completed_orders'] = all_orders.filter(current_status='seamstress_finished').count()
        
        # Count overdue orders
        from django.utils import timezone
        overdue_count = 0
        for order in all_orders:
            if order.is_overdue:
                overdue_count += 1
        context['overdue_orders'] = overdue_count
        
        context['status_choices'] = Order.STATUS_CHOICES
        context['item_type_choices'] = Order.ITEM_TYPE_CHOICES
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', 'all')
        context['item_type_filter'] = self.request.GET.get('item_type', 'all')
        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        
        # Get process steps
        context['process_steps'] = order.process_steps.all().order_by('created_at')
        
        # Get progress percentage
        context['progress_percentage'] = order.progress_percentage
        
        # Get status colors for display
        context['status_colors'] = {
            'seamstress_finished': 'bg-green-100 text-green-800',
            'customer_first_fitting': 'bg-yellow-100 text-yellow-800',
            'customer_second_fitting': 'bg-yellow-100 text-yellow-800',
            'cutter_cutting': 'bg-yellow-100 text-yellow-800',
            'order_placed': 'bg-blue-100 text-blue-800',
            'material_arrived': 'bg-blue-100 text-blue-800',
        }
        
        return context


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')
    
    def form_valid(self, form):
        # Generate order number in format: ORD-YYYYMM-001
        from datetime import datetime
        
        # Get current year and month
        now = datetime.now()
        year_month = now.strftime('%Y%m')  # e.g., 202510
        
        # Find the last order number for this month
        prefix = f"ORD-{year_month}-"
        last_order_this_month = Order.objects.filter(
            order_number__startswith=prefix
        ).order_by('-order_number').first()
        
        if last_order_this_month:
            # Extract the sequence number from the last order
            try:
                last_seq = int(last_order_this_month.order_number.split('-')[-1])
                next_seq = last_seq + 1
            except (ValueError, IndexError):
                next_seq = 1
        else:
            next_seq = 1
        
        # Generate new order number
        order_number = f"{prefix}{next_seq:03d}"
        
        form.instance.order_number = order_number
        form.instance.created_by = self.request.user
        
        messages.success(self.request, 'Захиалга амжилттай үүсгэгдлээ.')
        return super().form_valid(form)


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    
    def get_success_url(self):
        return reverse_lazy('orders:order_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Захиалга амжилттай шинэчлэгдлээ.')
        return super().form_valid(form)


class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('orders:order_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Захиалга амжилттай устгагдлаа.')
        return super().delete(request, *args, **kwargs)


@login_required
def advance_order_status(request, pk):
    """Advance order to next status"""
    from employees.models import Employee
    from django.utils import timezone
    
    order = get_object_or_404(Order, pk=pk)
    
    status_choices = [choice[0] for choice in Order.STATUS_CHOICES]
    current_index = status_choices.index(order.current_status)
    
    if current_index < len(status_choices) - 1:
        next_status = status_choices[current_index + 1]
        
        # Get the currently logged-in user's employee record if it exists
        completed_by = None
        if request.user.is_authenticated:
            try:
                # Try to get the employee associated with the current user
                completed_by = Employee.objects.get(user=request.user)
            except Employee.DoesNotExist:
                # If no employee found, try to find an employee based on status
                if order.current_status in ['order_placed', 'material_arrived']:
                    completed_by = Employee.objects.filter(employee_type__in=['shirt_sewer', 'jacket_sewer', 'trouser_sewer']).first()
                elif order.current_status in ['cutter_cutting']:
                    completed_by = Employee.objects.filter(employee_type='cutter').first()
                elif order.current_status in ['customer_first_fitting', 'customer_second_fitting']:
                    completed_by = None  # Customer action
                elif order.current_status in ['tailor_first_completion', 'tailor_second_completion']:
                    completed_by = Employee.objects.filter(employee_type__in=['shirt_sewer', 'jacket_sewer', 'trouser_sewer']).first()
                elif order.current_status in ['seamstress_second_prep', 'seamstress_finished']:
                    completed_by = Employee.objects.filter(employee_type__in=['shirt_sewer', 'jacket_sewer', 'trouser_sewer']).first()
        
        # Create status history for current status
        OrderStatusHistory.objects.create(
            order=order,
            status=order.current_status,
            completed_by=completed_by,
            completed_at=timezone.now(),
            notes=f'Алхам дууссан - {order.status_display}'
        )
        
        # Update order status
        order.current_status = next_status
        order.save()
        
        # If order is finished, set completed date
        if next_status == 'seamstress_finished':
            order.completed_date = timezone.now().date()
            order.save()
        
        messages.success(request, f'Захиалгын статус "{order.status_display}" болж шинэчлэгдлээ.')
    else:
        messages.info(request, 'Захиалга аль хэдийн дууссан байна.')
    
    return redirect('orders:order_detail', pk=order.pk)


@login_required
def update_process_step(request, pk):
    """Update process step status"""
    if request.method == 'POST':
        step_id = request.POST.get('step_id')
        new_status = request.POST.get('status')
        
        try:
            step = ProcessStep.objects.get(id=step_id, order_id=pk)
            step.status = new_status
            
            if new_status == 'completed':
                step.completed_date = timezone.now()
            
            step.save()
            
            # Update order status if this was the last step
            order = get_object_or_404(Order, pk=pk)
            if step.step_type == 'seamstress_finished' and new_status == 'completed':
                order.current_status = 'seamstress_finished'
                order.completed_date = timezone.now().date()
                order.save()
            
            return JsonResponse({'success': True, 'message': 'Алхам амжилттай шинэчлэгдлээ.'})
        
        except ProcessStep.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Алхам олдсонгүй.'})
    
    return JsonResponse({'success': False, 'message': 'Хүсэлт буруу байна.'})


@login_required
def rate_employee(request, pk):
    """Rate an employee for an order"""
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        try:
            employee = Employee.objects.get(pk=employee_id)
            
            # Create or update rating
            employee_rating, created = EmployeeRating.objects.get_or_create(
                order=order,
                employee=employee,
                defaults={'rating': rating, 'comment': comment}
            )
            
            if not created:
                employee_rating.rating = rating
                employee_rating.comment = comment
                employee_rating.save()
            
            messages.success(request, f'{employee.full_name}-д үнэлгээ амжилттай өглөө.')
            return redirect('orders:order_detail', pk=order.pk)
        
        except Employee.DoesNotExist:
            messages.error(request, 'Ажилтан олдсонгүй.')
            return redirect('orders:order_detail', pk=order.pk)
        except ValueError:
            messages.error(request, 'Үнэлгээ 1-5 хооронд байх ёстой.')
            return redirect('orders:order_detail', pk=order.pk)
    
    return redirect('orders:order_detail', pk=order.pk)


@login_required
def active_orders(request):
    """View for active/incomplete orders with search by phone"""
    queryset = Order.objects.select_related('customer').exclude(current_status='seamstress_finished')
    
    # Search by phone number
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(customer__phone__icontains=search_query)
    
    # Sort: overdue first, then by creation date
    orders = list(queryset.order_by('-created_at'))
    orders.sort(key=lambda x: (not x.is_overdue, x.created_at), reverse=True)
    
    # Get statistics
    total_active = len(orders)
    overdue_count = sum(1 for order in orders if order.is_overdue)
    
    context = {
        'orders': orders,
        'total_active': total_active,
        'overdue_count': overdue_count,
        'search_query': search_query,
    }
    
    return render(request, 'orders/active_orders.html', context)