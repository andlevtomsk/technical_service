from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from maintenance.models import Equipment, MaintenanceStandard, MaintenancePlan

class Command(BaseCommand):
    help = 'Генерация планов технического обслуживания для всего оборудования'

    def add_arguments(self, parser):
        parser.add_argument(
            '--years',
            type=int,
            default=3,
            help='Количество лет для планирования (по умолчанию: 3)'
        )

    def handle(self, *args, **options):
        years = options['years']
        self.stdout.write(f'Генерация планов на {years} лет вперед...')
        
        total_created = 0
        
        for equipment in Equipment.objects.all():
            created = self.generate_plans_for_equipment(equipment, years)
            total_created += created
        
        self.stdout.write(
            self.style.SUCCESS(f'Создано {total_created} новых планов!')
        )
    # Генерация планов для конкретного оборудования
    def generate_plans_for_equipment(self, equipment, years=3):
        standards = MaintenanceStandard.objects.filter(
            equipment_type=equipment.equipment_type
        )
        
        plans_created = 0
        months_ahead = years * 12
        
        for standard in standards:
            if standard.frequency_months <= 0:
                continue
                
            # Проверяем, есть ли уже планы
            existing_plans = MaintenancePlan.objects.filter(
                equipment=equipment,
                maintenance_type=standard.maintenance_type
            ).count()
            
            # Если планов мало или нет, создаем новые
            if existing_plans < (months_ahead // standard.frequency_months):
                num_plans = months_ahead // standard.frequency_months
                
                # Находим дату последнего плана или используем дату ввода
                last_plan = MaintenancePlan.objects.filter(
                    equipment=equipment,
                    maintenance_type=standard.maintenance_type
                ).order_by('-planned_date').first()
                
                if last_plan:
                    start_date = last_plan.planned_date
                    start_period = 1
                else:
                    start_date = equipment.installation_date
                    start_period = 0
                
                for i in range(start_period, num_plans + 1):
                    if i == 0:  # Пропускаем нулевой период
                        continue
                        
                    planned_date = start_date + timedelta(
                        days=standard.frequency_months * 30 * i
                    )
                    
                    # Проверяем, не существует ли уже такой план
                    if not MaintenancePlan.objects.filter(
                        equipment=equipment,
                        maintenance_type=standard.maintenance_type,
                        planned_date=planned_date
                    ).exists():
                        
                        MaintenancePlan.objects.create(
                            equipment=equipment,
                            maintenance_type=standard.maintenance_type,
                            planned_date=planned_date,
                            status='planned'
                        )
                        plans_created += 1
        
        if plans_created > 0:
            self.stdout.write(f'  {equipment.name}: создано {plans_created} планов')
        
        return plans_created