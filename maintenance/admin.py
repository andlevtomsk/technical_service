from django.contrib import admin
from .models import EquipmentType, Equipment, MaintenanceType, MaintenanceStandard, MaintenancePlan


@admin.register(EquipmentType)
class EquipmentTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'inventory_number', 'equipment_type', 'installation_date']
    list_filter = ['equipment_type']
    search_fields = ['name', 'inventory_number']


@admin.register(MaintenanceType)
class MaintenanceTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']


@admin.register(MaintenanceStandard)
class MaintenanceStandardAdmin(admin.ModelAdmin):
    list_display = ['equipment_type', 'maintenance_type', 'frequency_months']
    list_filter = ['equipment_type', 'maintenance_type']


@admin.register(MaintenancePlan)
class MaintenancePlanAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'maintenance_type', 'planned_date', 'actual_date', 'status']
    list_filter = ['status', 'maintenance_type', 'planned_date']
    search_fields = ['equipment__name', 'equipment__inventory_number']
