from django.urls import path

from . import views

urlpatterns = [
    path('bank-accounts/', views.BankAccountListCreateView.as_view()),
    path('bank-accounts/<int:pk>/', views.BankAccountDetailView.as_view()),
    path('expense-categories/', views.ExpenseCategoryListCreateView.as_view()),
    path('expense-categories/<int:pk>/', views.ExpenseCategoryDetailView.as_view()),
    path('expenses/', views.ExpenseListCreateView.as_view()),
    path('expenses/<int:pk>/', views.ExpenseDetailView.as_view()),
    path('payments/', views.PaymentListCreateView.as_view()),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view()),
    path('cashflows/', views.CashflowListCreateView.as_view()),
    path('cashflows/<int:pk>/', views.CashflowDetailView.as_view()),
    path('budgets/', views.BudgetListCreateView.as_view()),
    path('budgets/<int:pk>/', views.BudgetDetailView.as_view()),
    path('taxes/', views.TaxListCreateView.as_view()),
    path('taxes/<int:pk>/', views.TaxDetailView.as_view()),
    path('income-categories/', views.IncomeCategoryListCreateView.as_view()),
    path('income-categories/<int:pk>/', views.IncomeCategoryDetailView.as_view()),
    path('incomes/', views.IncomeListCreateView.as_view()),
    path('incomes/<int:pk>/', views.IncomeDetailView.as_view()),
    path('purchase-taxes/', views.PurchaseTaxListCreateView.as_view()),
    path('purchase-taxes/<int:pk>/', views.PurchaseTaxDetailView.as_view()),
    path('payrolls/', views.PayrollListCreateView.as_view()),
    path('payrolls/<int:pk>/', views.PayrollDetailView.as_view()),
    path('reports/expense-summary/', views.ExpenseSummaryView.as_view()),
    path('reports/income-summary/', views.IncomeSummaryView.as_view()),
    path('reports/profit-loss/', views.ProfitLossView.as_view()),
    path('reports/income-vs-expense/', views.IncomeVsExpenseView.as_view()),
    path('reports/tax-summary/', views.TaxSummaryView.as_view()),
]
