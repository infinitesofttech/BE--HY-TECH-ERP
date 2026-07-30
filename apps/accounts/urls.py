from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('register-device/', views.RegisterDeviceTokenView.as_view(), name='register-device'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('devices/', views.DeviceListView.as_view(), name='device-list'),
    path('employees/', views.EmployeeListView.as_view(), name='employee-list'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/toggle-active/', views.EmployeeToggleActiveView.as_view(), name='employee-toggle-active'),
    path('contact/', views.ContactInfoView.as_view(), name='contact-info'),
    path('feedback/', views.FeedbackCreateView.as_view(), name='feedback-create'),
    path('feedback/list/', views.FeedbackListView.as_view(), name='feedback-list'),
    path('2fa/enable/', views.TwoFactorEnableView.as_view(), name='2fa-enable'),
    path('2fa/verify/', views.TwoFactorVerifyView.as_view(), name='2fa-verify'),
    path('verify-email/', views.EmailVerificationRequestView.as_view(), name='verify-email'),
    path('verify-email/confirm/', views.EmailVerificationConfirmView.as_view(), name='verify-email-confirm'),
    path('delete-request/', views.DeleteAccountRequestView.as_view(), name='delete-request'),
]
