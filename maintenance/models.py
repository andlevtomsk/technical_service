from django.db import models
from django.contrib.auth.models import User


class EquipmentType(models.Model):
    name = models.CharField(max_length=200, verbose_name="Тип оборудования")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип оборудования"
        verbose_name_plural = "Типы оборудования"


class Equipment(models.Model):
    name = models.CharField(max_length=200, verbose_name="Наименование")
    inventory_number = models.CharField(max_length=50, unique=True, verbose_name="Инвентарный номер")
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE, verbose_name="Тип оборудования")
    installation_date = models.DateField(verbose_name="Дата ввода в эксплуатацию")

    def __str__(self):
        return f"{self.name} ({self.inventory_number})"

    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"


class MaintenanceType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Вид обслуживания")
    code = models.CharField(max_length=10, verbose_name="Код", unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Вид обслуживания"
        verbose_name_plural = "Виды обслуживания"


class MaintenanceStandard(models.Model):
    equipment_type = models.ForeignKey(EquipmentType, on_delete=models.CASCADE, verbose_name="Тип оборудования")
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.CASCADE, verbose_name="Вид обслуживания")
    frequency_months = models.IntegerField(verbose_name="Периодичность (месяцев)")

    def __str__(self):
        return f"{self.equipment_type} - {self.maintenance_type}"

    class Meta:
        verbose_name = "Норматив обслуживания"
        verbose_name_plural = "Нормативы обслуживания"
        unique_together = ['equipment_type', 'maintenance_type']


class MaintenancePlan(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Запланировано'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнено'),
        ('cancelled', 'Отменено'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, verbose_name="Оборудование")
    maintenance_type = models.ForeignKey(MaintenanceType, on_delete=models.CASCADE, verbose_name="Вид обслуживания")
    planned_date = models.DateField(verbose_name="Плановая дата")
    actual_date = models.DateField(null=True, blank=True, verbose_name="Фактическая дата")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned', verbose_name="Статус")
    notes = models.TextField(blank=True, verbose_name="Примечания")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='created_plans', verbose_name="Кем создано")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='updated_plans', verbose_name="Кем изменено")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    def __str__(self):
        return f"{self.equipment} - {self.maintenance_type} - {self.planned_date}"

    class Meta:
        verbose_name = "План обслуживания"
        verbose_name_plural = "Планы обслуживания"
        ordering = ['planned_date']


# Отслеживание продления планов обслуживания
class MaintenancePlanExtension(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, verbose_name="Оборудование")
    last_extension_date = models.DateField(verbose_name="Дата последнего продления")
    next_extension_date = models.DateField(verbose_name="Дата следующего продления")
    extension_years = models.IntegerField(default=3, verbose_name="Лет на продление")

    def __str__(self):
        return f"Продление для {self.equipment.name} до {self.next_extension_date}"

    class Meta:
        verbose_name = "Продление планов"
        verbose_name_plural = "Продления планов"
