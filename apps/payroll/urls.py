from django.urls import path
from .views import (
    PayrollListCreateAPIView,
    PayrollSummaryAPIView,
    PayrollDetailAPIView,
    SalarySlipAPIView,
    ExpenseListCreateAPIView,
    ExpenseDetailAPIView,
    FinanceSummaryAPIView,
    AllHistoryAPIView,
    IncomeHistoryAPIView,
    ExpenseHistoryAPIView,
)

urlpatterns = [
    # Payroll
    path('summary/', PayrollSummaryAPIView.as_view(), name='payroll-summary'),
    path('expenses/', ExpenseListCreateAPIView.as_view(), name='expense-list-create'),
    path('expenses/<int:pk>/', ExpenseDetailAPIView.as_view(), name='expense-detail'),
    path('finance/', FinanceSummaryAPIView.as_view(), name='finance-summary'),
    path('history/all/', AllHistoryAPIView.as_view(), name='finance-all-history'),
    path('history/income/', IncomeHistoryAPIView.as_view(), name='finance-income-history'),
    path('history/expense/', ExpenseHistoryAPIView.as_view(), name='finance-expense-history'),
    path('', PayrollListCreateAPIView.as_view(), name='payroll-list-create'),
    path('<int:pk>/salary-slip/', SalarySlipAPIView.as_view(), name='payroll-salary-slip'),
    path('<int:pk>/', PayrollDetailAPIView.as_view(), name='payroll-detail'),
]
