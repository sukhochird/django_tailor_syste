from django.core.management.base import BaseCommand
from orders.models import Order, OrderStatusHistory
from employees.models import Employee
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Fix order data and add status history'

    def handle(self, *args, **options):
        # Get employees
        employees = list(Employee.objects.all())
        if not employees:
            self.stdout.write(self.style.ERROR('No employees found. Please create employees first.'))
            return

        # Fix each order by adding appropriate status history
        orders = Order.objects.all()
        
        for order in orders:
            self.stdout.write(f'Processing {order.order_number}...')
            
            # Clear existing history
            order.status_history.all().delete()
            
            # Get status choices in order
            status_choices = [choice[0] for choice in order.STATUS_CHOICES]
            current_index = status_choices.index(order.current_status)
            
            # Add history for all completed statuses
            for i, status_code in enumerate(status_choices[:current_index + 1]):
                # Determine who completed this step
                completed_by = None
                if status_code in ['order_placed', 'material_arrived']:
                    completed_by = employees[0] if employees else None
                elif status_code in ['cutter_cutting']:
                    completed_by = next((emp for emp in employees if emp.employee_type == 'cutter'), employees[0])
                elif status_code in ['customer_first_fitting', 'customer_second_fitting']:
                    completed_by = None  # Customer action
                elif status_code in ['tailor_first_completion', 'tailor_second_completion']:
                    completed_by = next((emp for emp in employees if emp.employee_type == 'tailor'), employees[0])
                elif status_code in ['seamstress_second_prep', 'seamstress_finished']:
                    completed_by = next((emp for emp in employees if emp.employee_type == 'tailor'), employees[0])
                
                # Calculate completion time (spread over time)
                days_ago = current_index - i
                completed_at = datetime.now() - timedelta(days=days_ago)
                
                # Create status history
                OrderStatusHistory.objects.create(
                    order=order,
                    status=status_code,
                    completed_by=completed_by,
                    completed_at=completed_at,
                    notes=f'Алхам {i+1} дууссан'
                )
                
                self.stdout.write(f'  Added history for {status_code}')
            
            # If order is finished, mark it as completed
            if order.current_status == 'seamstress_finished':
                order.completed_date = datetime.now().date()
                order.save()
                self.stdout.write(f'  Marked {order.order_number} as completed')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully fixed {orders.count()} orders with status history'
            )
        )
