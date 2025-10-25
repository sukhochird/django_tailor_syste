from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from orders.models import Order, OrderStatusHistory
from customers.models import Customer
from employees.models import Employee
from materials.models import Material
from decimal import Decimal
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Create dummy order data'

    def handle(self, *args, **options):
        # Create superuser if doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created admin user'))

        # Create customers
        customers_data = [
            {'full_name': 'Батбаяр', 'phone': '99112233', 'email': 'batbayar@example.com', 'customer_type': 'regular'},
            {'full_name': 'Сараа', 'phone': '99223344', 'email': 'saraa@example.com', 'customer_type': 'vip'},
            {'full_name': 'Энхтуяа', 'phone': '99334455', 'email': 'enkhtuya@example.com', 'customer_type': 'regular'},
            {'full_name': 'Мөнхбаяр', 'phone': '99445566', 'email': 'monkhbayar@example.com', 'customer_type': 'vip'},
            {'full_name': 'Цэцэг', 'phone': '99556677', 'email': 'tseveg@example.com', 'customer_type': 'regular'},
            {'full_name': 'Болд', 'phone': '99667788', 'email': 'bold@example.com', 'customer_type': 'vip'},
            {'full_name': 'Алтанцэцэг', 'phone': '99778899', 'email': 'altantsetseg@example.com', 'customer_type': 'regular'},
            {'full_name': 'Ганбаяр', 'phone': '99889900', 'email': 'ganbayar@example.com', 'customer_type': 'vip'},
        ]

        customers = []
        for customer_data in customers_data:
            customer, created = Customer.objects.get_or_create(
                phone=customer_data['phone'],
                defaults=customer_data
            )
            customers.append(customer)
            if created:
                self.stdout.write(f'Created customer: {customer.full_name}')

        # Create employees
        employees_data = [
            {'full_name': 'Эсгүүрчин 1', 'position': 'cutter', 'phone': '88112233'},
            {'full_name': 'Эсгүүрчин 2', 'position': 'cutter', 'phone': '88223344'},
            {'full_name': 'Оёдолчин 1', 'position': 'seamstress', 'phone': '88334455'},
            {'full_name': 'Оёдолчин 2', 'position': 'seamstress', 'phone': '88445566'},
            {'full_name': 'Миллэгч 1', 'position': 'tailor', 'phone': '88556677'},
            {'full_name': 'Миллэгч 2', 'position': 'tailor', 'phone': '88667788'},
        ]

        employees = []
        for employee_data in employees_data:
            employee, created = Employee.objects.get_or_create(
                phone=employee_data['phone'],
                defaults=employee_data
            )
            employees.append(employee)
            if created:
                self.stdout.write(f'Created employee: {employee.full_name}')

        # Create materials
        materials_data = [
            {'name': 'Хөвөн даавуу', 'unit_price': Decimal('15000.00'), 'unit': 'метр', 'stock_quantity': Decimal('100.00'), 'supplier': 'Текстиль ХХК'},
            {'name': 'Шелк даавуу', 'unit_price': Decimal('25000.00'), 'unit': 'метр', 'stock_quantity': Decimal('50.00'), 'supplier': 'Шелк ХХК'},
            {'name': 'Шинэ даавуу', 'unit_price': Decimal('18000.00'), 'unit': 'метр', 'stock_quantity': Decimal('75.00'), 'supplier': 'Шинэ ХХК'},
            {'name': 'Хөвөн даавуу 2', 'unit_price': Decimal('12000.00'), 'unit': 'метр', 'stock_quantity': Decimal('80.00'), 'supplier': 'Текстиль ХХК'},
            {'name': 'Шелк даавуу 2', 'unit_price': Decimal('30000.00'), 'unit': 'метр', 'stock_quantity': Decimal('30.00'), 'supplier': 'Шелк ХХК'},
        ]

        materials = []
        for material_data in materials_data:
            material, created = Material.objects.get_or_create(
                name=material_data['name'],
                defaults=material_data
            )
            materials.append(material)
            if created:
                self.stdout.write(f'Created material: {material.name}')

        # Create orders
        order_data = [
            {
                'customer': customers[0],
                'item_type': 'Цамц',
                'material': materials[0],
                'total_amount': Decimal('75000.00'),
                'start_date': datetime.now().date(),
                'due_date': (datetime.now() + timedelta(days=7)).date(),
                'current_status': 'order_placed',
                'notes': 'Хөвөн даавуутай цамц'
            },
            {
                'customer': customers[1],
                'item_type': 'Өмд',
                'material': materials[1],
                'total_amount': Decimal('95000.00'),
                'start_date': datetime.now().date(),
                'due_date': (datetime.now() + timedelta(days=10)).date(),
                'current_status': 'material_arrived',
                'notes': 'Шелк даавуутай өмд'
            },
            {
                'customer': customers[2],
                'item_type': 'Хувцас',
                'material': materials[2],
                'total_amount': Decimal('120000.00'),
                'start_date': (datetime.now() - timedelta(days=2)).date(),
                'due_date': (datetime.now() + timedelta(days=5)).date(),
                'current_status': 'cutter_cutting',
                'notes': 'Шинэ даавуутай хувцас'
            },
            {
                'customer': customers[3],
                'item_type': 'Цамц',
                'material': materials[3],
                'total_amount': Decimal('65000.00'),
                'start_date': (datetime.now() - timedelta(days=5)).date(),
                'due_date': (datetime.now() + timedelta(days=2)).date(),
                'current_status': 'customer_first_fitting',
                'notes': 'Хөвөн даавуутай цамц'
            },
            {
                'customer': customers[4],
                'item_type': 'Өмд',
                'material': materials[4],
                'total_amount': Decimal('150000.00'),
                'start_date': (datetime.now() - timedelta(days=8)).date(),
                'due_date': (datetime.now() - timedelta(days=1)).date(),
                'current_status': 'tailor_first_completion',
                'notes': 'Шелк даавуутай өмд'
            },
            {
                'customer': customers[5],
                'item_type': 'Хувцас',
                'material': materials[0],
                'total_amount': Decimal('180000.00'),
                'start_date': (datetime.now() - timedelta(days=12)).date(),
                'due_date': (datetime.now() - timedelta(days=3)).date(),
                'current_status': 'seamstress_second_prep',
                'notes': 'Хөвөн даавуутай хувцас'
            },
            {
                'customer': customers[6],
                'item_type': 'Цамц',
                'material': materials[1],
                'total_amount': Decimal('85000.00'),
                'start_date': (datetime.now() - timedelta(days=15)).date(),
                'due_date': (datetime.now() - timedelta(days=5)).date(),
                'current_status': 'customer_second_fitting',
                'notes': 'Шелк даавуутай цамц'
            },
            {
                'customer': customers[7],
                'item_type': 'Өмд',
                'material': materials[2],
                'total_amount': Decimal('110000.00'),
                'start_date': (datetime.now() - timedelta(days=18)).date(),
                'due_date': (datetime.now() - timedelta(days=8)).date(),
                'current_status': 'tailor_second_completion',
                'notes': 'Шинэ даавуутай өмд'
            },
            {
                'customer': customers[0],
                'item_type': 'Хувцас',
                'material': materials[3],
                'total_amount': Decimal('140000.00'),
                'start_date': (datetime.now() - timedelta(days=20)).date(),
                'due_date': (datetime.now() - timedelta(days=10)).date(),
                'current_status': 'seamstress_finished',
                'notes': 'Хөвөн даавуутай хувцас'
            },
            {
                'customer': customers[1],
                'item_type': 'Цамц',
                'material': materials[4],
                'total_amount': Decimal('200000.00'),
                'start_date': (datetime.now() - timedelta(days=25)).date(),
                'due_date': (datetime.now() - timedelta(days=15)).date(),
                'current_status': 'seamstress_finished',
                'notes': 'Шелк даавуутай цамц'
            }
        ]

        orders = []
        for order_info in order_data:
            order, created = Order.objects.get_or_create(
                customer=order_info['customer'],
                item_type=order_info['item_type'],
                material=order_info['material'],
                defaults=order_info
            )
            orders.append(order)
            if created:
                self.stdout.write(f'Created order: {order.order_number}')

        # Create status history for some orders
        status_histories = [
            {
                'order': orders[1],  # material_arrived
                'status': 'order_placed',
                'completed_by': employees[0],
                'completed_at': datetime.now() - timedelta(days=1),
                'notes': 'Захиалга бүртгэгдлээ'
            },
            {
                'order': orders[2],  # cutter_cutting
                'status': 'order_placed',
                'completed_by': employees[0],
                'completed_at': datetime.now() - timedelta(days=2),
                'notes': 'Захиалга бүртгэгдлээ'
            },
            {
                'order': orders[2],
                'status': 'material_arrived',
                'completed_by': employees[1],
                'completed_at': datetime.now() - timedelta(days=1),
                'notes': 'Материал ирлээ'
            },
            {
                'order': orders[3],  # customer_first_fitting
                'status': 'order_placed',
                'completed_by': employees[0],
                'completed_at': datetime.now() - timedelta(days=5),
                'notes': 'Захиалга бүртгэгдлээ'
            },
            {
                'order': orders[3],
                'status': 'material_arrived',
                'completed_by': employees[1],
                'completed_at': datetime.now() - timedelta(days=4),
                'notes': 'Материал ирлээ'
            },
            {
                'order': orders[3],
                'status': 'cutter_cutting',
                'completed_by': employees[0],
                'completed_at': datetime.now() - timedelta(days=3),
                'notes': 'Эсгэж дууслаа'
            },
        ]

        for history_data in status_histories:
            OrderStatusHistory.objects.get_or_create(
                order=history_data['order'],
                status=history_data['status'],
                defaults=history_data
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'- {len(customers)} customers\n'
                f'- {len(employees)} employees\n'
                f'- {len(materials)} materials\n'
                f'- {len(orders)} orders\n'
                f'- {len(status_histories)} status history records'
            )
        )
