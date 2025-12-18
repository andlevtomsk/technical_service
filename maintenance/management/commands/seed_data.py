from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from maintenance.models import EquipmentType, Equipment, MaintenanceType, MaintenanceStandard, MaintenancePlan
import random

class Command(BaseCommand):
    help = 'Заполнение базы данных тестовыми данными согласно ТЗ'

    def handle(self, *args, **options):
        self.stdout.write('Начало заполнения базы тестовыми данными...')
        
        # Очистка существующих данных
        self.clear_data()
        
        # Создание типов оборудования
        equipment_types = self.create_equipment_types()
        
        # Создание видов обслуживания
        maintenance_types = self.create_maintenance_types()
        
        # Создание нормативов обслуживания
        self.create_maintenance_standards(equipment_types, maintenance_types)
        
        # Создание оборудования
        equipments = self.create_equipments(equipment_types)
        
        # Создание планов обслуживания
        self.create_maintenance_plans(equipments, maintenance_types)
        
        self.stdout.write(
            self.style.SUCCESS('База данных успешно заполнена тестовыми данными!')
        )
    # Очистка существующих данных
    def clear_data(self):
        MaintenancePlan.objects.all().delete()
        MaintenanceStandard.objects.all().delete()
        Equipment.objects.all().delete()
        EquipmentType.objects.all().delete()
        MaintenanceType.objects.all().delete()
    # Создание типов оборудования
    def create_equipment_types(self):
        equipment_types_data = [
            'Токарный станок',
            'Фрезерный станок с ЧПУ',
            'Пресс гидравлический',
            'Конвейер ленточный',
            'Компрессор винтовой',
            'Сушильная камера',
            'Шлифовальный станок',
            'Сварочный аппарат'
        ]
        
        equipment_types = []
        for name in equipment_types_data:
            eq_type, created = EquipmentType.objects.get_or_create(name=name)
            equipment_types.append(eq_type)
            self.stdout.write(f'Создан тип оборудования: {name}')
        
        return equipment_types
    # Создание видов обслуживания согласно ТЗ
    def create_maintenance_types(self):
        maintenance_types_data = [
            {'name': 'Технический осмотр', 'code': 'ТО'},
            {'name': 'Технический ремонт', 'code': 'ТР'},
            {'name': 'Капитальный ремонт', 'code': 'КР'}
        ]
        
        maintenance_types = []
        for data in maintenance_types_data:
            mt, created = MaintenanceType.objects.get_or_create(
                name=data['name'],
                code=data['code']
            )
            maintenance_types.append(mt)
            self.stdout.write(f'Создан вид обслуживания: {data["name"]} ({data["code"]})')
        
        return maintenance_types
    # Создание нормативов обслуживания согласно ТЗ
    def create_maintenance_standards(self, equipment_types, maintenance_types):
        standards_data = {
            'ТО': 1,    # 1 месяц
            'ТР': 6,    # 6 месяцев
            'КР': 36    # 3 года = 36 месяцев
        }
        
        for equipment_type in equipment_types:
            for maintenance_type in maintenance_types:
                frequency = standards_data.get(maintenance_type.code)
                if frequency:
                    standard, created = MaintenanceStandard.objects.get_or_create(
                        equipment_type=equipment_type,
                        maintenance_type=maintenance_type,
                        frequency_months=frequency
                    )
                    self.stdout.write(
                        f'Создан норматив: {equipment_type.name} - {maintenance_type.name} '
                        f'({frequency} мес.)'
                    )
    # Создание оборудования
    def create_equipments(self, equipment_types):
        equipments_data = [
            # Токарные станки
            {'name': 'Токарный станок 1К62', 'inventory_number': 'STANK-001', 'type_idx': 0},
            {'name': 'Токарный станок 16К20', 'inventory_number': 'STANK-002', 'type_idx': 0},
            {'name': 'Токарный станок с ЧПУ', 'inventory_number': 'STANK-003', 'type_idx': 0},
            
            # Фрезерные станки
            {'name': 'Фрезерный станок 6Р13', 'inventory_number': 'FREZ-001', 'type_idx': 1},
            {'name': 'Фрезерный станок Haas', 'inventory_number': 'FREZ-002', 'type_idx': 1},
            
            # Прессы
            {'name': 'Пресс гидравлический 50т', 'inventory_number': 'PRESS-001', 'type_idx': 2},
            {'name': 'Пресс гидравлический 100т', 'inventory_number': 'PRESS-002', 'type_idx': 2},
            
            # Конвейеры
            {'name': 'Конвейер главный', 'inventory_number': 'CONV-001', 'type_idx': 3},
            {'name': 'Конвейер упаковочный', 'inventory_number': 'CONV-002', 'type_idx': 3},
            
            # Компрессоры
            {'name': 'Компрессор Atlas Copco', 'inventory_number': 'COMP-001', 'type_idx': 4},
            
            # Сушильные камеры
            {'name': 'Сушильная камера СК-5', 'inventory_number': 'DRY-001', 'type_idx': 5},
            
            # Шлифовальные станки
            {'name': 'Шлифовальный станок 3Г71', 'inventory_number': 'GRIND-001', 'type_idx': 6},
            
            # Сварочные аппараты
            {'name': 'Сварочный аппарат Kemppi', 'inventory_number': 'WELD-001', 'type_idx': 7},
            {'name': 'Сварочный аппарат ESAB', 'inventory_number': 'WELD-002', 'type_idx': 7},
        ]
        
        equipments = []
        base_date = timezone.now().date() - timedelta(days=180) 
        
        for data in equipments_data:
            equipment = Equipment.objects.create(
                name=data['name'],
                inventory_number=data['inventory_number'],
                equipment_type=equipment_types[data['type_idx']],
                installation_date=base_date - timedelta(days=random.randint(0, 365))
            )
            equipments.append(equipment)
            self.stdout.write(f'Создано оборудование: {data["name"]} ({data["inventory_number"]})')
        
        return equipments
    # Создание планов обслуживания
    def create_maintenance_plans(self, equipments, maintenance_types):
        self.stdout.write('Создание планов обслуживания...')
        
        # Получаем нормативы
        standards = MaintenanceStandard.objects.all()
        
        for equipment in equipments:
            equipment_standards = standards.filter(equipment_type=equipment.equipment_type)
            
            for standard in equipment_standards:
                months_ahead = 24
                frequency = standard.frequency_months
                
                for period in range(1, (months_ahead // frequency) + 1):
                    planned_date = equipment.installation_date + timedelta(days=frequency * 30 * period)
                    
                    if planned_date < timezone.now().date() - timedelta(days=30):
                        continue
                    
                    status_weights = {
                        'planned': 0.7,
                        'in_progress': 0.1,
                        'completed': 0.15,
                        'cancelled': 0.05
                    }
                    
                    status = random.choices(
                        list(status_weights.keys()),
                        weights=list(status_weights.values())
                    )[0]
                    
                    actual_date = None
                    if status == 'completed':
                        actual_date = planned_date + timedelta(days=random.randint(-5, 2))
                    
                    plan = MaintenancePlan.objects.create(
                        equipment=equipment,
                        maintenance_type=standard.maintenance_type,
                        planned_date=planned_date,
                        actual_date=actual_date,
                        status=status,
                        notes=self.generate_notes(standard.maintenance_type, status)
                    )
                    
                    self.stdout.write(
                        f'  Создан план: {equipment.name} - {standard.maintenance_type.name} '
                        f'на {planned_date} ({plan.get_status_display()})'
                    )
    # Генерация примечаний в зависимости от вида обслуживания и статуса
    def generate_notes(self, maintenance_type, status):
        notes_templates = {
            'ТО': {
                'planned': 'Запланирован технический осмотр согласно графику',
                'in_progress': 'Проводится визуальный осмотр и проверка параметров',
                'completed': 'Технический осмотр выполнен. Замечаний нет.',
                'cancelled': 'Осмотр перенесен в связи с производственной необходимостью'
            },
            'ТР': {
                'planned': 'Запланирован технический ремонт по графику',
                'in_progress': 'Выполняется замена изношенных деталей и регулировка',
                'completed': 'Технический ремонт завершен. Оборудование готово к работе.',
                'cancelled': 'Ремонт перенесен на следующий период'
            },
            'КР': {
                'planned': 'Запланирован капитальный ремонт оборудования',
                'in_progress': 'Выполняется полная разборка и замена основных узлов',
                'completed': 'Капитальный ремонт выполнен. Оборудование прошло испытания.',
                'cancelled': 'Капитальный ремонт отложен по техническим причинам'
            }
        }
        
        template = notes_templates.get(maintenance_type.code, {}).get(status, '')
        return template