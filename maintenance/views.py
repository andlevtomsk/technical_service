from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import views as auth_views
from datetime import timedelta
from .models import Equipment, MaintenancePlan
from .forms import EquipmentForm, MaintenancePlanForm, MaintenancePlanEditForm


# Главная страница с календарем
@login_required
def index(request):
    return render(request, 'maintenance/index.html')


# Список оборудования
@login_required
def equipment_list(request):
    equipments = Equipment.objects.all().select_related('equipment_type')
    return render(request, 'maintenance/equipment_list.html', {'equipments': equipments})


# Добавление нового оборудования
@login_required
def equipment_add(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            equipment = form.save()

            create_maintenance_plans(equipment)

            messages.success(request, 'Оборудование успешно добавлено! Планы обслуживания сгенерированы.')
            return redirect('equipment_list')
    else:
        form = EquipmentForm()
    return render(request, 'maintenance/equipment_form.html', {'form': form})


# Автоматическое создание планов обслуживания для нового оборудования
def create_maintenance_plans(equipment):
    from .models import MaintenanceStandard, MaintenancePlan

    # Получаем нормативы для типа оборудования
    standards = MaintenanceStandard.objects.filter(
        equipment_type=equipment.equipment_type
    )

    plans_created = 0

    for standard in standards:
        if standard.frequency_months <= 0:
            continue

        # Создаем планы на 3 года вперед (36 месяцев)
        months_ahead = 36
        num_plans = months_ahead // standard.frequency_months

        for i in range(1, num_plans + 1):
            planned_date = equipment.installation_date + timedelta(
                days=standard.frequency_months * 30 * i
            )

            # Создаем план
            MaintenancePlan.objects.create(
                equipment=equipment,
                maintenance_type=standard.maintenance_type,
                planned_date=planned_date,
                status='planned'
            )
            plans_created += 1

    return plans_created


# Список планов обслуживания
@login_required
def maintenance_plan_list(request):
    plans = MaintenancePlan.objects.all().select_related('equipment', 'maintenance_type')
    return render(request, 'maintenance/maintenance_plan_list.html', {'plans': plans})


# Добавление плана обслуживания
@login_required
def maintenance_plan_add(request):
    if request.method == 'POST':
        form = MaintenancePlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.created_by = request.user
            plan.save()
            messages.success(request, 'План обслуживания успешно создан!')
            return redirect('maintenance_plan_list')
    else:
        form = MaintenancePlanForm()
    return render(request, 'maintenance/maintenance_plan_form.html', {'form': form})


# Редактирование плана обслуживания
@login_required
def maintenance_plan_edit(request, pk):
    plan = get_object_or_404(MaintenancePlan, pk=pk)
    if request.method == 'POST':
        form = MaintenancePlanEditForm(request.POST, instance=plan)
        if form.is_valid():
            updated_plan = form.save(commit=False)
            updated_plan.updated_by = request.user

            if updated_plan.status == 'completed' and not updated_plan.actual_date:
                updated_plan.actual_date = timezone.now().date()

            updated_plan.save()
            messages.success(request, 'План обслуживания успешно обновлен!')
            return redirect('maintenance_plan_list')
    else:
        form = MaintenancePlanEditForm(instance=plan)

    return render(request, 'maintenance/maintenance_plan_edit.html', {
        'form': form,
        'plan': plan
    })


# Удаление плана обслуживания
@login_required
def maintenance_plan_delete(request, pk):
    plan = get_object_or_404(MaintenancePlan, pk=pk)
    if request.method == 'POST':
        equipment_name = plan.equipment.name
        plan.delete()
        messages.success(request, f'План обслуживания для "{equipment_name}" успешно удален!')
        return redirect('maintenance_plan_list')

    return render(request, 'maintenance/maintenance_plan_confirm_delete.html', {'plan': plan})


# Профиль пользователя
@login_required
def profile(request):
    user_plans_created = MaintenancePlan.objects.filter(created_by=request.user).count()
    user_plans_updated = MaintenancePlan.objects.filter(updated_by=request.user).count()

    recent_created = MaintenancePlan.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    recent_updated = MaintenancePlan.objects.filter(updated_by=request.user).exclude(created_by=request.user).order_by(
        '-updated_at')[:5]

    return render(request, 'maintenance/profile.html', {
        'user_plans_created': user_plans_created,
        'user_plans_updated': user_plans_updated,
        'recent_created': recent_created,
        'recent_updated': recent_updated,
    })


# API для получения ВСЕХ данных календаря
@login_required
def calendar_all_data(request):
    try:
        plans = MaintenancePlan.objects.all().select_related('equipment', 'maintenance_type')
        print(f"Всего планов в базе: {plans.count()}")

        events = []
        for plan in plans:
            if plan.status == 'completed':
                color = '#28a745'
            elif plan.status == 'in_progress':
                color = '#ffc107'
            elif plan.status == 'cancelled':
                color = '#dc3545'
            else:
                if plan.maintenance_type.code == 'ТО':
                    color = '#007bff'
                elif plan.maintenance_type.code == 'ТР':
                    color = '#fd7e14'
                else:
                    color = '#6f42c1'

            events.append({
                'id': plan.id,
                'title': f"{plan.equipment.name} - {plan.maintenance_type.name}",
                'start': plan.planned_date.isoformat(),
                'color': color,
                'textColor': 'white',
                'extendedProps': {
                    'equipment': plan.equipment.name,
                    'maintenance_type': plan.maintenance_type.name,
                    'status': plan.get_status_display(),
                    'inventory_number': plan.equipment.inventory_number,
                    'created_by': plan.created_by.username if plan.created_by else 'Система',
                    'updated_by': plan.updated_by.username if plan.updated_by else 'Не изменялся',
                }
            })

        print(f"Возвращаем {len(events)} событий")
        return JsonResponse(events, safe=False)

    except Exception as e:
        print(f"Ошибка: {e}")
        return JsonResponse({'error': str(e)}, status=500)


def login_view(request):
    return auth_views.LoginView.as_view(template_name='maintenance/login.html')(request)


def logout_view(request):
    if request.method == 'POST':
        messages.info(request, 'Вы успешно вышли из системы.')
    return auth_views.LogoutView.as_view()(request)
