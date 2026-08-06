from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('company/register/', views.CompanyRegisterView.as_view(), name='company-register'),
    path('company/profile/', views.CompanyProfileView.as_view(), name='company-profile'),
    path('company/dashboard/', views.CompanyDashboardView.as_view(), name='company-dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('register-device/', views.RegisterDeviceTokenView.as_view(), name='register-device'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('devices/', views.DeviceListView.as_view(), name='device-list'),
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/toggle-active/', views.EmployeeToggleActiveView.as_view(), name='employee-toggle-active'),
    path('contact/', views.ContactInfoView.as_view(), name='contact-info'),
    path('feedback/', views.FeedbackCreateView.as_view(), name='feedback-create'),
    path('feedback/list/', views.FeedbackListView.as_view(), name='feedback-list'),
    path('delete-request/', views.DeleteAccountRequestView.as_view(), name='delete-request'),
    path('roles/', views.RoleListCreateView.as_view(), name='role-list'),
    path('roles/<int:pk>/', views.RoleDetailView.as_view(), name='role-detail'),
    path('login-logs/', views.LoginLogListView.as_view(), name='login-log-list'),
    path('activity-logs/', views.UserActivityLogListCreateView.as_view(), name='activity-log-list'),
]
