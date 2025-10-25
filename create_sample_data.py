#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta, datetime
from decimal import Decimal
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tailor_system.settings')
django.setup()

from customers.models import Customer
from employees.models import Employee
from orders.models import Order

def create_sample_data():
    print("Creating sample data...")
    
    # Get or create customers
    customers_data = [
        {'first_name': 'Болд', 'last_name': 'Батбаяр', 'phone': '99112233', 'email': 'bold.batbayar@email.com', 'customer_type': 'vip'},
        {'first_name': 'Сарантуяа', 'last_name': 'Доржийн', 'phone': '99223344', 'email': 'sarantuya.dorjin@email.com', 'customer_type': 'regular'},
        {'first_name': 'Мөнхбат', 'last_name': 'Цэрэндоржийн', 'phone': '99334455', 'email': 'munkhbat.tserendorjin@email.com', 'customer_type': 'vip'},
        {'first_name': 'Энхтуяа', 'last_name': 'Оюунчимэг', 'phone': '99445566', 'email': 'enkhtuya.oyunchimeg@email.com', 'customer_type': 'regular'},
        {'first_name': 'Цэцэгт', 'last_name': 'Алтангэрэлийн', 'phone': '99556677', 'email': 'tsetseg.altangerel@email.com', 'customer_type': 'vip'},
        {'first_name': 'Батбаяр', 'last_name': 'Мөнххүү', 'phone': '99667788', 'email': 'batbayar.munkhhuu@email.com', 'customer_type': 'regular'},
        {'first_name': 'Энхцэцэг', 'last_name': 'Сүхбаатарын', 'phone': '99778899', 'email': 'enkhtsetseg.sukhbaatar@email.com', 'customer_type': 'regular'},
        {'first_name': 'Наранбаатар', 'last_name': 'Жигмэдийн', 'phone': '99889911', 'email': 'naranbaatar.jigmed@email.com', 'customer_type': 'vip'},
        {'first_name': 'Мөнхзул', 'last_name': 'Очирбатын', 'phone': '99912233', 'email': 'munkhzul.ochirbat@email.com', 'customer_type': 'regular'},
        {'first_name': 'Отгонбат', 'last_name': 'Ганбаатарын', 'phone': '99001234', 'email': 'otgonbat.ganbaatar@email.com', 'customer_type': 'regular'},
        {'first_name': 'Уранцэцэг', 'last_name': 'Баатарын', 'phone': '99221133', 'email': 'urantsetseg.baatar@email.com', 'customer_type': 'regular'},
        {'first_name': 'Дорж', 'last_name': 'Энхбаярын', 'phone': '99332244', 'email': 'dorj.enkhbayar@email.com', 'customer_type': 'vip'},
        {'first_name': 'Цэцэгмаа', 'last_name': 'Лхамсүрэнийн', 'phone': '99443355', 'email': 'tsetsegmaa.lhamsuren@email.com', 'customer_type': 'regular'},
        {'first_name': 'Очир', 'last_name': 'Доржпалмаагийн', 'phone': '99554466', 'email': 'ochir.dorjpalmaa@email.com', 'customer_type': 'regular'},
        {'first_name': 'Мөнхөө', 'last_name': 'Цогтбаярын', 'phone': '99665577', 'email': 'munkhoo.tsogtbayar@email.com', 'customer_type': 'vip'},
    ]
    
    customers = []
    for customer_data in customers_data:
        customer, created = Customer.objects.get_or_create(
            phone=customer_data['phone'],
            defaults=customer_data
        )
        customers.append(customer)
        if created:
            print(f"Created customer: {customer.full_name}")
    
    # Get or create employees
    employees_data = [
        {'first_name': 'Батбаяр', 'last_name': 'Сүхбаатар', 'phone': '+976 9911-1234', 'employee_type': 'jacket_sewer'},
        {'first_name': 'Цэцэгмаа', 'last_name': 'Доржсүрэн', 'phone': '+976 9922-5678', 'employee_type': 'cutter'},
        {'first_name': 'Мөнхбаяр', 'last_name': 'Очирбат', 'phone': '+976 9876-5432', 'employee_type': 'trouser_sewer'},
        {'first_name': 'Мөнгөндэр', 'last_name': 'Лхамсүрэн', 'phone': '+976 9933-9999', 'employee_type': 'shirt_sewer'},
        {'first_name': 'Наранцэцэг', 'last_name': 'Баатар', 'phone': '+976 9944-7777', 'employee_type': 'cutter'},
    ]
    
    employees = []
    for employee_data in employees_data:
        employee, created = Employee.objects.get_or_create(
            phone=employee_data['phone'],
            defaults=employee_data
        )
        employees.append(employee)
        if created:
            print(f"Created employee: {employee.full_name}")
    
    # Generate 20 orders with various statuses
    today = date.today()
    statuses = [
        'order_placed',
        'material_arrived',
        'cutter_cutting',
        'customer_first_fitting',
        'tailor_first_completion',
        'seamstress_second_prep',
        'customer_second_fitting',
        'tailor_second_completion',
    ]
    
    item_types = [
        'men_suit',
        'women_suit',
        'wedding_dress',
        'formal_dress',
        'casual_shirt',
        'trousers',
        'jacket',
        'vest',
        'coat',
        'repair',
    ]
    
    material_codes = ['MAT-001', 'MAT-002', 'MAT-003', 'MAT-004', 'MAT-005', 'MAT-006']
    
    orders_created = 0
    order_counter = 1
    while orders_created < 20:
        # Generate order number
        order_number = f"ORD-{today.strftime('%Y%m')}-{order_counter:03d}"
        
        # Skip if order already exists
        if Order.objects.filter(order_number=order_number).exists():
            print(f"Order {order_number} already exists, skipping...")
            order_counter += 1
            continue
        
        # Random data
        customer = random.choice(customers)
        status = random.choice(statuses)
        item_type = random.choice(item_types)
        
        # Calculate dates based on status
        days_ago = random.randint(1, 30)
        start_date = today - timedelta(days=days_ago)
        due_date = start_date + timedelta(days=random.randint(7, 21))
        
        # Check if overdue
        is_overdue = due_date < today
        
        # Assign employees based on type
        assigned_tailor = random.choice([emp for emp in employees if emp.employee_type in ['jacket_sewer', 'shirt_sewer', 'trouser_sewer']])
        assigned_cutter = random.choice([emp for emp in employees if emp.employee_type == 'cutter'])
        assigned_trouser_maker = random.choice([emp for emp in employees if emp.employee_type == 'trouser_sewer'])
        
        # Amount based on item type
        amounts = {
            'men_suit': Decimal('450000'),
            'women_suit': Decimal('380000'),
            'wedding_dress': Decimal('650000'),
            'formal_dress': Decimal('280000'),
            'casual_shirt': Decimal('65000'),
            'trousers': Decimal('85000'),
            'jacket': Decimal('180000'),
            'vest': Decimal('75000'),
            'coat': Decimal('320000'),
            'repair': Decimal('25000'),
        }
        total_amount = amounts.get(item_type, Decimal('100000'))
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            order_number=order_number,
            item_type=item_type,
            material_code=random.choice(material_codes),
            assigned_tailor=assigned_tailor,
            assigned_cutter=assigned_cutter,
            assigned_trouser_maker=assigned_trouser_maker,
            total_amount=total_amount,
            start_date=start_date,
            due_date=due_date,
            current_status=status,
            notes=f'Тест захиалга #{order_counter}'
        )
        
        print(f"Created order: {order.order_number} - {order.get_current_status_display()} - {order.customer.full_name}")
        orders_created += 1
        order_counter += 1
    
    print(f"\n✅ Successfully created {orders_created} orders with various statuses!")
    print(f"📊 Status distribution:")
    for status_code, status_label in Order.STATUS_CHOICES:
        count = Order.objects.filter(current_status=status_code).count()
        if count > 0:
            print(f"   - {status_label}: {count}")

if __name__ == '__main__':
    create_sample_data()
