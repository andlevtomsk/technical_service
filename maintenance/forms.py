from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Equipment, MaintenancePlan


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'inventory_number', 'equipment_type', 'installation_date']
        widgets = {
            'installation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class MaintenancePlanForm(forms.ModelForm):
    class Meta:
        model = MaintenancePlan
        fields = ['equipment', 'maintenance_type', 'planned_date', 'status', 'actual_date', 'notes']
        widgets = {
            'planned_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'actual_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Введите примечания...'}),
            'equipment': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


# Форма для редактирования плана обслуживания
class MaintenancePlanEditForm(forms.ModelForm):
    class Meta:
        model = MaintenancePlan
        fields = ['status', 'actual_date', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'actual_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Введите примечания...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.status == 'completed' and not self.instance.actual_date:
            self.fields['actual_date'].required = True


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Имя пользователя'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )
