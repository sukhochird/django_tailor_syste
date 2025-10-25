from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView
from django.db.models import Count, Sum, Q
from django.db import models
from orders.models import Order


class SuperuserRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure only superusers can access"""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.warning(request, 'Та энэ хуудсанд хандах эрхгүй байна.')
            return redirect('orders:order_list')
        return super().dispatch(request, *args, **kwargs)


class MaterialListView(SuperuserRequiredMixin, ListView):
    """Material report view based on Order material codes"""
    template_name = 'materials/material_list.html'
    context_object_name = 'materials'
    paginate_by = 20
    
    def get_queryset(self):
        """Generate material statistics from Order material codes"""
        from django.db.models import Count, Sum, Case, When, IntegerField, DecimalField
        
        # Get all orders with material codes
        orders = Order.objects.exclude(material_code__isnull=True).exclude(material_code='')
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            orders = orders.filter(material_code__icontains=search_query)
        
        # Group by material code and calculate statistics
        material_stats = orders.values('material_code').annotate(
            total_orders=Count('id'),
            completed_orders=Count('id', filter=Q(current_status='seamstress_finished')),
            active_orders=Count('id', filter=~Q(current_status='seamstress_finished')),
        ).order_by('-total_orders')
        
        # Add additional calculated fields
        for material in material_stats:
            # Check if material is frequently used (more than 2 orders)
            material['is_frequently_used'] = material['total_orders'] >= 2
        
        return material_stats
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get summary statistics
        all_orders = Order.objects.exclude(material_code__isnull=True).exclude(material_code='')
        
        context['search_query'] = self.request.GET.get('search', '')
        context['total_materials'] = all_orders.values('material_code').distinct().count()
        context['total_orders_with_materials'] = all_orders.count()
        context['completed_with_materials'] = all_orders.filter(
            current_status='seamstress_finished'
        ).count()
        
        return context