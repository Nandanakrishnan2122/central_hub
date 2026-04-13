from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path(
        '',
        auth_views.LoginView.as_view(
            template_name='login.html',
            redirect_authenticated_user=True
        )
    ),
    path('index/', views.index, name='index'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='login.html',
            redirect_authenticated_user=True
        ),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout'
    ),
    path('register/', views.register_view, name='register'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path("principal/dashboard/", views.dashboard, name="principal_dashboard"),
    path("user/dashboard/", views.dashboard, name="user_dashboard"),

    path('departments/', views.department_list, name='department_list'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/delete/<int:pk>/', views.delete_department, name='delete_department'),
    path('departments/edit/<int:pk>/', views.edit_department, name='edit_department'),
    path('department/<int:department_id>/devices/', views.department_devices, name='department_devices'),
    path('department/<int:department_id>/<str:device_type>/',views.department_devices_by_type,name='department_devices_by_type'),
    path('department/<int:department_id>/device-types-pdf/',views.download_department_device_types_pdf,name='download_department_device_types_pdf'),
    path('department/<int:department_id>/<str:device_type>/devices-pdf/',views.download_department_devices_pdf,name='download_department_devices_pdf'),
    
    path('devices/', views.device_list, name='device_list'),
    #path('device/<int:device_id>/', views.device_detail, name='device_detail'),
    path('devices/add/', views.add_device, name='add_device'),
    


    path('device-locations/', views.device_location_list, name='device_location_list'),

    path('issues/', views.issue_list, name='issue_list'),
    path('issue/report/<int:device_id>/', views.report_issue, name='report_issue'),
    path('issue/<int:issue_id>/', views.issue_detail, name='issue_detail'),
    path('issue/solve/<int:pk>/', views.issue_solved, name='issue_solved'),
    path('issues/solved/', views.solved_issue_list, name='solved_issue_list'),
    path('issues/solved/edit/<int:pk>/', views.edit_solved_issue, name='edit_solved_issue'),
    path('issues/solved/delete/<int:pk>/', views.delete_solved_issue, name='delete_solved_issue'),
    path('issues/solved/<int:pk>/', views.solved_issue_detail, name='solved_issue_detail'),
    path('issues/solved/<int:pk>/pdf/',views.download_solved_issue_pdf,name='download_solved_issue_pdf'),
    path('issues/solved/pdf/',views.download_solved_issue_list_pdf,name='download_solved_issue_list_pdf'),
    path('issue/delete/<int:issue_id>/', views.delete_issue, name='delete_issue'),
    path(
    'issues/reported/pdf/',
    views.download_issue_list_pdf,
    name='download_issue_list_pdf'
),
    
    
    
    path('device-types/', views.device_type_list, name='device_type_list'),
    path('device/<int:device_id>/issues/', views.device_issues, name='device_issues'),
    path('device/<int:pk>/', views.device_detail, name='device_detail'),
    path('device/edit/<int:pk>/', views.edit_device, name='edit_device'),
    path('device/<int:pk>/pdf/', views.download_device_pdf, name='download_device_pdf'),
    path("devices/pdf/", views.download_devices_pdf, name="download_devices_pdf"),
    path('device/delete/<int:device_id>/', views.delete_device, name='delete_device'),
    path('device/<int:device_id>/report-history/',views.device_report_history,name='device_report_history'),
    path('device/<int:device_id>/report-history/pdf/',views.download_device_report_history_pdf,name='download_device_report_history_pdf'),
    path('device-type/add/', views.add_device_type, name='add_device_type'),
    path('device-type/delete/<int:id>/', views.delete_device_type, name='delete_device_type'),
    path('device/delete/<int:id>/', views.delete_device, name='delete_device'),

    path('analytics/devices/', views.device_analytics, name='device_analytics'),
    path('analytics/issues/', views.issue_analytics, name='issue_analytics'),
    path('analytics/solved/', views.solved_analytics, name='solved_analytics'),
    path('analytics/working/', views.working_analytics, name='working_analytics'),

    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/edit/<int:pk>/', views.edit_user, name='edit_user'),
    path('user/delete/<int:user_id>/',views.delete_user,name='delete_user'),
    path('users/<int:id>/', views.user_details, name='user_details'),
    
    path('about/', views.about, name='about'),

    path('notifications/', views.notifications, name='notifications'),
]



