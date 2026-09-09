from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.finance.models import (
    BankAccount,
    ExpenseCategory, Expense,
    Payment,
    Cashflow,
    Budget,
    Tax,
    IncomeCategory, Income,
    PurchaseTax,
    Payroll,
)
from apps.invoices.models import Invoice
from apps.products.models import Product, ProductCategory
from apps.purchases.models import Purchase, PurchaseOrder, Vendor
from apps.sales.models import Customer, SalesOrder, SalesOrderItem


class FinanceModelTests(TestCase):
    def setUp(self):
        self.expense_cat = ExpenseCategory.objects.create(name='Fuel')
        self.income_cat = IncomeCategory.objects.create(name='Sales')
        self.tax = Tax.objects.create(name='VAT', rate=18)

    def test_auto_ids(self):
        expense = Expense.objects.create(
            name='Diesel', category=self.expense_cat,
            amount=100, date=date(2026, 7, 1),
        )
        self.assertTrue(expense.expense_id.startswith('EXP-'))
        payment = Payment.objects.create(
            payee='Vendor A', amount=50, date=date(2026, 7, 1),
        )
        self.assertTrue(payment.payment_id.startswith('PAY-'))
        cashflow = Cashflow.objects.create(
            type='inflow', amount=200, date=date(2026, 7, 1),
        )
        self.assertTrue(cashflow.ref_id.startswith('CF-'))
        income = Income.objects.create(
            party_name='Customer A', category=self.income_cat,
            amount=500, date=date(2026, 7, 1),
        )
        self.assertTrue(income.income_id.startswith('INC-'))
        budget = Budget.objects.create(
            period='Q3 2026', category=self.expense_cat, budget=1000,
        )
        self.assertTrue(budget.budget_id.startswith('BUD-'))
        self.assertTrue(self.tax.tax_id.startswith('TAX-'))

    def test_budget_spent_computed(self):
        budget = Budget.objects.create(
            period='Q3 2026', category=self.expense_cat, budget=1000,
        )
        Expense.objects.create(
            name='Diesel', category=self.expense_cat, amount=200,
            date=date(2026, 7, 15), status='paid',
        )
        Expense.objects.create(
            name='Tolls', category=self.expense_cat, amount=100,
            date=date(2026, 9, 15), status='approved',
        )
        Expense.objects.create(
            name='Pending', category=self.expense_cat, amount=300,
            date=date(2026, 7, 20), status='pending',
        )
        Expense.objects.create(
            name='Next quarter', category=self.expense_cat, amount=400,
            date=date(2026, 10, 15), status='paid',
        )
        self.assertEqual(budget.spent(), 300)
        self.assertEqual(budget.remaining(), 700)
        self.assertEqual(budget.usage_percent(), 30.0)

    def test_budget_period_validation(self):
        budget = Budget(
            period='Q9 2026', category=self.expense_cat, budget=100,
        )
        with self.assertRaises(Exception):
            budget.full_clean()


class FinanceAPITests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = get_user_model().objects.create_user(
            username='admin', email='admin@finance.test',
            password='testpass123', role='super_admin',
        )
        self.client = APIClient()
        self.expense_cat = ExpenseCategory.objects.create(name='Fuel')
        self.income_cat = IncomeCategory.objects.create(name='Sales')
        self.tax = Tax.objects.create(name='VAT', rate=18)

    def test_expense_summary(self):
        Expense.objects.create(
            name='Diesel', category=self.expense_cat, amount=200,
            payment_method='cash', date=date(2026, 7, 1), status='paid',
        )
        Expense.objects.create(
            name='Parking', category=self.expense_cat, amount=50,
            payment_method='card', date=date(2026, 7, 2), status='pending',
        )
        vendor = Vendor.objects.create(name='Vendor A')
        Purchase.objects.create(
            vendor=vendor, date=date(2026, 7, 3),
            status='paid', total_amount=100,
        )
        Purchase.objects.create(
            vendor=vendor, date=date(2026, 7, 4),
            status='pending', total_amount=500,
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            '/api/finance/reports/expense-summary/'
            '?date_from=2026-07-01&date_to=2026-07-31',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_expense'], 300.0)
        self.assertEqual(response.data['finance_expense'], 200.0)
        self.assertEqual(response.data['purchase_expense'], 100.0)
        self.assertEqual(response.data['average_expense'], 150.0)
        self.assertEqual(response.data['highest_category']['name'], 'Fuel')
        self.assertEqual(response.data['top_vendor']['name'], 'Vendor A')
        self.assertEqual(response.data['sources']['purchases']['total'], 100.0)
        self.assertEqual(len(response.data['expenses']), 2)

    def test_expense_summary_includes_received_purchase_orders(self):
        vendor = Vendor.objects.create(name='Vendor B')
        PurchaseOrder.objects.create(
            vendor=vendor, order_date=date(2026, 7, 5),
            status='received', total_amount=300,
        )
        PurchaseOrder.objects.create(
            vendor=vendor, order_date=date(2026, 7, 6),
            status='pending', total_amount=900,
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            '/api/finance/reports/expense-summary/'
            '?date_from=2026-07-01&date_to=2026-07-31',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_expense'], 300.0)
        self.assertEqual(response.data['purchase_expense'], 300.0)
        self.assertEqual(response.data['sources']['purchase_orders']['total'], 300.0)
        self.assertEqual(response.data['sources']['purchase_orders']['count'], 1)
        self.assertEqual(response.data['top_vendor']['name'], 'Vendor B')
        self.assertEqual(len(response.data['expenses']), 1)
        self.assertEqual(response.data['expenses'][0]['source'], 'purchase_order')

    def test_expense_summary_filters_purchase_orders_by_status(self):
        vendor = Vendor.objects.create(name='Vendor C')
        PurchaseOrder.objects.create(
            vendor=vendor, order_date=date(2026, 7, 5),
            status='received', total_amount=300,
        )
        PurchaseOrder.objects.create(
            vendor=vendor, order_date=date(2026, 7, 6),
            status='partially_paid', total_amount=700,
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            '/api/finance/reports/expense-summary/'
            '?date_from=2026-07-01&date_to=2026-07-31&status=received',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['purchase_expense'], 300.0)
        self.assertEqual(response.data['sources']['purchase_orders']['count'], 1)

    def test_income_summary_with_growth(self):
        Income.objects.create(
            party_name='Customer A', category=self.income_cat, amount=500,
            payment_method='bank_transfer', date=date(2026, 7, 1),
            status='received',
        )
        Income.objects.create(
            party_name='Customer B', category=self.income_cat, amount=300,
            payment_method='cash', date=date(2026, 6, 1),
            status='received',
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            '/api/finance/reports/income-summary/'
            '?date_from=2026-07-01&date_to=2026-07-31',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_income'], 500.0)
        self.assertEqual(response.data['income_growth'], 66.67)
        self.assertEqual(len(response.data['incomes']), 1)

    def test_income_summary_includes_sales_and_invoices(self):
        Income.objects.create(
            party_name='Customer A', category=self.income_cat, amount=100,
            payment_method='bank_transfer', date=date(2026, 7, 5),
            status='received',
        )
        customer = Customer.objects.create(name='Walk-in')
        SalesOrder.objects.create(
            customer=customer, date=date(2026, 7, 6),
            status='completed', payment_method='cash', total_amount=250,
        )
        SalesOrder.objects.create(
            customer=customer, date=date(2026, 7, 7),
            status='in_progress', payment_method='cash', total_amount=999,
        )
        Invoice.objects.create(
            invoice_number='INV-001', customer_name='Corp Ltd',
            invoice_date=date(2026, 7, 8), due_date=date(2026, 8, 8),
            status='paid', total=150,
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            '/api/finance/reports/income-summary/'
            '?date_from=2026-07-01&date_to=2026-07-31',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_income'], 500.0)
        self.assertEqual(response.data['finance_income'], 100.0)
        self.assertEqual(response.data['sales_income'], 250.0)
        self.assertEqual(response.data['invoice_income'], 150.0)
        self.assertEqual(response.data['sources']['sales_orders']['count'], 1)
        self.assertEqual(len(response.data['incomes']), 3)

    def test_profit_loss(self):
        Expense.objects.create(
            name='Rent', category=self.expense_cat, amount=200,
            date=date(2026, 7, 1), status='paid',
        )
        Income.objects.create(
            party_name='Customer A', category=self.income_cat, amount=500,
            date=date(2026, 7, 1), status='received',
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            '/api/finance/reports/profit-loss/'
            '?date_from=2026-07-01&date_to=2026-07-31',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_revenue'], 500.0)
        self.assertEqual(response.data['total_expense'], 200.0)
        self.assertEqual(response.data['net_profit'], 300.0)
        self.assertEqual(response.data['margin_percent'], 60.0)

    def test_profit_loss_across_modules(self):
        Expense.objects.create(
            name='Rent', category=self.expense_cat, amount=200,
            date=date(2026, 7, 1), status='paid',
        )
        Income.objects.create(
            party_name='Customer A', category=self.income_cat, amount=500,
            date=date(2026, 7, 1), status='received',
        )
        customer = Customer.objects.create(name='Walk-in')
        SalesOrder.objects.create(
            customer=customer, date=date(2026, 7, 2),
            status='completed', total_amount=300,
        )
        vendor = Vendor.objects.create(name='Vendor A')
        Purchase.objects.create(
            vendor=vendor, date=date(2026, 7, 3),
            status='paid', total_amount=150,
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            '/api/finance/reports/profit-loss/'
            '?date_from=2026-07-01&date_to=2026-07-31',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_revenue'], 800.0)
        self.assertEqual(response.data['total_expense'], 350.0)
        self.assertEqual(response.data['net_profit'], 450.0)
        self.assertEqual(response.data['revenue_sources']['sales_orders'], 300.0)
        self.assertEqual(response.data['expense_sources']['purchases'], 150.0)

    def test_income_vs_expense_monthly(self):
        Expense.objects.create(
            name='Rent', category=self.expense_cat, amount=100,
            date=date(2026, 7, 1), status='paid',
        )
        Income.objects.create(
            party_name='Customer A', category=self.income_cat, amount=300,
            date=date(2026, 7, 15), status='received',
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            '/api/finance/reports/income-vs-expense/'
            '?date_from=2026-07-01&date_to=2026-07-31&group_by=month',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_income'], 300.0)
        self.assertEqual(response.data['total_expense'], 100.0)
        self.assertEqual(response.data['net_difference'], 200.0)
        self.assertEqual(response.data['expense_ratio'], 33.33)
        self.assertEqual(response.data['periods'][0]['trend'], '+')
        self.assertEqual(response.data['periods'][0]['period'], '2026-07')

    def test_income_vs_expense_includes_sales_and_purchases(self):
        Expense.objects.create(
            name='Rent', category=self.expense_cat, amount=100,
            date=date(2026, 7, 1), status='paid',
        )
        Income.objects.create(
            party_name='Customer A', category=self.income_cat, amount=300,
            date=date(2026, 7, 15), status='received',
        )
        customer = Customer.objects.create(name='Walk-in')
        SalesOrder.objects.create(
            customer=customer, date=date(2026, 7, 10),
            status='completed', total_amount=200,
        )
        vendor = Vendor.objects.create(name='Vendor A')
        Purchase.objects.create(
            vendor=vendor, date=date(2026, 7, 12),
            status='paid', total_amount=50,
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            '/api/finance/reports/income-vs-expense/'
            '?date_from=2026-07-01&date_to=2026-07-31&group_by=month',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_income'], 500.0)
        self.assertEqual(response.data['total_expense'], 150.0)
        self.assertEqual(response.data['net_difference'], 350.0)
        self.assertEqual(
            response.data['sources']['income']['sales_orders'], 200.0,
        )
        self.assertEqual(
            response.data['sources']['expense']['purchases'], 50.0,
        )
        self.assertEqual(response.data['periods'][0]['income'], 500.0)
        self.assertEqual(response.data['periods'][0]['expense'], 150.0)

    def test_tax_summary(self):
        PurchaseTax.objects.create(
            bill_id='BILL-1', supplier='Supplier A', tax_type=self.tax,
            tax_amount=36, payment_method='bank_transfer',
            date=date(2026, 7, 1), status='completed',
        )
        Invoice.objects.create(
            invoice_number='INV-001', customer_name='Corp Ltd',
            invoice_date=date(2026, 7, 5), due_date=date(2026, 8, 5),
            status='paid', total=118, tax=self.tax, tax_amount=18,
        )
        customer = Customer.objects.create(name='Walk-in')
        category = ProductCategory.objects.create(name='Parts')
        product = Product.objects.create(
            name='Brake Pad', category=category, price=100,
        )
        order = SalesOrder.objects.create(
            customer=customer, date=date(2026, 7, 6),
            status='completed', total_amount=118,
        )
        SalesOrderItem.objects.create(
            order=order, product=product, quantity=1,
            unit_price=100, amount=100, tax=self.tax, tax_amount=18,
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(
            '/api/finance/reports/tax-summary/'
            '?date_from=2026-07-01&date_to=2026-07-31',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_purchase_tax'], 36.0)
        self.assertEqual(response.data['avg_tax_per_purchase'], 36.0)
        self.assertEqual(
            response.data['highest_tax_category']['name'], 'VAT',
        )
        self.assertEqual(response.data['taxes'][0]['supplier'], 'Supplier A')
        self.assertEqual(response.data['total_sales_tax'], 18.0)
        self.assertEqual(response.data['total_invoice_tax'], 18.0)
        self.assertEqual(response.data['total_collected_tax'], 36.0)
        self.assertEqual(response.data['net_tax'], 0.0)
        self.assertEqual(response.data['tax_breakdown'][0]['collected'], 36.0)
        self.assertEqual(response.data['tax_breakdown'][0]['paid'], 36.0)

    def test_reports_require_auth(self):
        response = self.client.get('/api/finance/reports/profit-loss/')
        self.assertEqual(response.status_code, 401)

    def test_budget_reads(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(
            '/api/finance/budgets/',
            {
                'period': 'Q3 2026',
                'category': self.expense_cat.id,
                'budget': '1000.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['budget_id'][:4], 'BUD-')
        self.assertEqual(response.data['spent'], 0.0)
        self.assertEqual(response.data['usage_percent'], 0.0)

        response = self.client.post(
            '/api/finance/budgets/',
            {
                'period': 'Q9 2026',
                'category': self.expense_cat.id,
                'budget': '1000.00',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_payroll_create_computes_totals(self):
        self.client.force_authenticate(user=self.admin)
        employee = get_user_model().objects.create_user(
            username='emp', email='emp@payroll.test',
            password='testpass123', role='msr',
        )
        response = self.client.post(
            '/api/finance/payrolls/',
            {
                'employee': employee.id,
                'payroll_month': '2026-07',
                'payment_date': '2026-07-31',
                'basic_salary': '50000',
                'hra': '10000',
                'conveyance': '2000',
                'bonus': '5000',
                'other_allowance': '1000',
                'pf': '3000',
                'professional_tax': '200',
                'tds': '5000',
                'other_deductions': '300',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['payroll_id'][:3], 'PL-')
        self.assertEqual(response.data['employee'], employee.id)
        self.assertEqual(float(response.data['total_earning']), 68000.0)
        self.assertEqual(float(response.data['total_deduction']), 8500.0)
        self.assertEqual(float(response.data['net_salary']), 59500.0)
        self.assertEqual(response.data['status'], 'pending')

    def test_payroll_update_and_filter(self):
        self.client.force_authenticate(user=self.admin)
        employee = get_user_model().objects.create_user(
            username='emp', email='emp2@payroll.test',
            password='testpass123', role='msr',
        )
        payroll = Payroll.objects.create(
            employee=employee, payroll_month='2026-07',
            basic_salary=30000, hra=5000,
        )
        self.assertEqual(payroll.total_earning, 35000)
        self.assertEqual(payroll.net_salary, 35000)

        response = self.client.patch(
            f'/api/finance/payrolls/{payroll.id}/',
            {'tds': '2000', 'status': 'paid'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'paid')
        self.assertEqual(float(response.data['total_deduction']), 2000.0)
        self.assertEqual(float(response.data['net_salary']), 33000.0)

        response = self.client.get(
            f'/api/finance/payrolls/?payroll_month=2026-07',
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
