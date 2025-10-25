from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Customer
from .forms import CustomerForm


class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Customer.objects.all().order_by('-created_at')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search_query) |
                models.Q(last_name__icontains=search_query) |
                models.Q(phone__icontains=search_query) |
                models.Q(email__icontains=search_query)
            )
        
        # Customer type filter
        customer_type_filter = self.request.GET.get('customer_type')
        if customer_type_filter and customer_type_filter != 'all':
            queryset = queryset.filter(customer_type=customer_type_filter)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer_type_choices'] = Customer.CUSTOMER_TYPE_CHOICES
        context['search_query'] = self.request.GET.get('search', '')
        context['customer_type_filter'] = self.request.GET.get('customer_type', 'all')
        
        # Summary statistics
        all_customers = Customer.objects.all()
        context['total_customers'] = all_customers.count()
        context['vip_customers'] = all_customers.filter(customer_type='vip').count()
        context['regular_customers'] = all_customers.filter(customer_type='regular').count()
        
        # This month's customers
        from django.utils import timezone
        from datetime import timedelta
        start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        context['this_month_customers'] = all_customers.filter(created_at__gte=start_of_month).count()
        
        return context


class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'customers/customer_detail.html'
    context_object_name = 'customer'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.get_object()
        
        # Get customer's orders
        orders = customer.order_set.all().order_by('-created_at')
        context['orders'] = orders
        
        # Calculate statistics
        context['total_orders'] = orders.count()
        context['completed_orders'] = orders.filter(current_status='seamstress_finished').count()
        context['active_orders'] = orders.exclude(current_status='seamstress_finished').count()
        
        return context


class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    success_url = reverse_lazy('customers:customer_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Үйлчлүүлэгч амжилттай бүртгэгдлээ.')
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        # Check if this is an AJAX request
        if request.headers.get('Content-Type') == 'application/json':
            import json
            data = json.loads(request.body)
            
            # Create customer manually
            try:
                customer = Customer.objects.create(
                    last_name=data.get('last_name'),
                    first_name=data.get('first_name'),
                    phone=data.get('phone'),
                    email=data.get('email', ''),
                    customer_type=data.get('customer_type', 'regular')
                )
                
                return JsonResponse({
                    'success': True,
                    'customer_id': customer.id,
                    'customer_name': customer.full_name
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
        
        # Regular form submission
        return super().post(request, *args, **kwargs)


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = 'customers/customer_form.html'
    
    def get_success_url(self):
        return reverse_lazy('customers:customer_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Үйлчлүүлэгчийн мэдээлэл амжилттай шинэчлэгдлээ.')
        return super().form_valid(form)


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'
    success_url = reverse_lazy('customers:customer_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Үйлчлүүлэгч амжилттай устгагдлаа.')
        return super().delete(request, *args, **kwargs)


@require_http_methods(["GET"])
def search_customers(request):
    """Search customers by phone number"""
    phone = request.GET.get('phone', '').strip()
    
    if not phone or len(phone) < 3:
        return JsonResponse({'customers': []})
    
    customers = Customer.objects.filter(phone__icontains=phone)[:10]
    
    results = []
    for customer in customers:
        results.append({
            'id': customer.id,
            'full_name': customer.full_name,
            'phone': customer.phone,
            'email': customer.email or '',
            'customer_type': customer.customer_type
        })
    
    return JsonResponse({'customers': results})