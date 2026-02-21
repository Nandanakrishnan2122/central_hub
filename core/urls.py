from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('index/', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('departments/', views.department_list, name='department_list'),

    path('devices/', views.device_list, name='device_list'),
    path('device/<int:device_id>/', views.device_detail, name='device_detail'),
    path('devices/add/', views.add_device, name='add_device'),


    path('device-locations/', views.device_location_list, name='device_location_list'),

    path('issues/', views.issue_list, name='issue_list'),
    path('issue/report/<int:device_id>/', views.report_issue, name='report_issue'),
    path('issue/<int:issue_id>/', views.issue_detail, name='issue_detail'),

    path('device-types/', views.device_type_list, name='device_type_list'),
    path('device-specs/', views.device_spec_list, name='device_spec_list'),
    path('users/', views.user_list, name='user_list'),
]
