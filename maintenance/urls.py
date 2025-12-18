from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/add/', views.equipment_add, name='equipment_add'),
    path('maintenance/', views.maintenance_plan_list, name='maintenance_plan_list'),
    path('maintenance/add/', views.maintenance_plan_add, name='maintenance_plan_add'),
    path('maintenance/<int:pk>/edit/', views.maintenance_plan_edit, name='maintenance_plan_edit'),
    path('maintenance/<int:pk>/delete/', views.maintenance_plan_delete, name='maintenance_plan_delete'),
    path('calendar/all/', views.calendar_all_data, name='calendar_all_data'),
    path('profile/', views.profile, name='profile'),

    path('login/', auth_views.LoginView.as_view(template_name='maintenance/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
]
