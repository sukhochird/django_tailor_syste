from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('active/', views.active_orders, name='active_orders'),
    path('new/', views.OrderCreateView.as_view(), name='order_create'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/edit/', views.OrderUpdateView.as_view(), name='order_edit'),
    path('<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),
    path('<int:pk>/advance-status/', views.advance_order_status, name='advance_status'),
    path('<int:pk>/update-step/', views.update_process_step, name='update_step'),
    path('<int:pk>/rate-employee/', views.rate_employee, name='rate_employee'),
]
