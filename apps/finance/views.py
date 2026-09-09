from datetime import datetime, timedelta

from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsManagerOrAbove
from apps.invoices.models import Invoice
from apps.purchases.models import Purchase, PurchaseOrder
from apps.sales.models import SalesOrder, SalesOrderItem
from apps.common.utils import parse_date_range

from .models import (
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
from .serializers import (
    BankAccountSerializer,
    ExpenseCategorySerializer, ExpenseSerializer,
    PaymentSerializer,
    CashflowSerializer,
    BudgetSerializer,
    TaxSerializer,
    IncomeCategorySerializer, IncomeSerializer,
    PurchaseTaxSerializer,
    PayrollSerializer,
)


class BankAccountListCreateView(generics.ListCreateAPIView):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class BankAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]


class ExpenseCategoryListCreateView(generics.ListCreateAPIView):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['status']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class ExpenseCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]


class ExpenseListCreateView(generics.ListCreateAPIView):
    queryset = Expense.objects.select_related('category').all()
    serializer_class = ExpenseSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['category', 'status', 'payment_method', 'date']
    search_fields = ['expense_id', 'name', 'description']
    ordering_fields = ['date', 'amount', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Expense.objects.select_related('category').all()
    serializer_class = ExpenseSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]


class PaymentListCreateView(generics.ListCreateAPIView):
    queryset = Payment.objects.select_related('bank').all()
    serializer_class = PaymentSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['bank', 'status', 'payment_method', 'date']
    search_fields = ['payment_id', 'payee']
    ordering_fields = ['date', 'amount', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.select_related('bank').all()
    serializer_class = PaymentSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]


class CashflowListCreateView(generics.ListCreateAPIView):
    queryset = Cashflow.objects.select_related('bank').all()
    serializer_class = CashflowSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['bank', 'type', 'status', 'payment_method', 'date']
    search_fields = ['ref_id']
    ordering_fields = ['date', 'amount', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class CashflowDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cashflow.objects.select_related('bank').all()
    serializer_class = CashflowSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]


class BudgetListCreateView(generics.ListCreateAPIView):
    queryset = Budget.objects.select_related('category').all()
    serializer_class = BudgetSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['category', 'period']
    search_fields = ['budget_id']
    ordering_fields = ['period', 'budget', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Budget.objects.select_related('category').all()
    serializer_class = BudgetSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]


class TaxListCreateView(generics.ListCreateAPIView):
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['status', 'applied_to']
    search_fields = ['tax_id', 'name']
    ordering_fields = ['name', 'rate', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class TaxDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]


class IncomeCategoryListCreateView(generics.ListCreateAPIView):
    queryset = IncomeCategory.objects.all()
    serializer_class = IncomeCategorySerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['status']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class IncomeCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = IncomeCategory.objects.all()
    serializer_class = IncomeCategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]


class IncomeListCreateView(generics.ListCreateAPIView):
    queryset = Income.objects.select_related('category').all()
    serializer_class = IncomeSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['category', 'status', 'payment_method', 'date']
    search_fields = ['income_id', 'party_name']
    ordering_fields = ['date', 'amount', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class IncomeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Income.objects.select_related('category').all()
    serializer_class = IncomeSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]


class PurchaseTaxListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseTax.objects.select_related('tax_type').all()
    serializer_class = PurchaseTaxSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['tax_type', 'status', 'payment_method', 'date']
    search_fields = ['bill_id', 'supplier']
    ordering_fields = ['date', 'tax_amount', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class PurchaseTaxDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseTax.objects.select_related('tax_type').all()
    serializer_class = PurchaseTaxSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]


class PayrollListCreateView(generics.ListCreateAPIView):
    queryset = Payroll.objects.select_related(
        'employee', 'designation', 'department',
    ).all()
    serializer_class = PayrollSerializer
    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,
    ]
    filterset_fields = ['employee', 'designation', 'department', 'payroll_month', 'status']
    search_fields = [
        'payroll_id', 'employee__email', 'employee__first_name',
        'employee__last_name',
    ]
    ordering_fields = ['payroll_month', 'payment_date', 'net_salary', 'created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsManagerOrAbove()]
        return [IsAuthenticated()]


class PayrollDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payroll.objects.select_related(
        'employee', 'designation', 'department',
    ).all()
    serializer_class = PayrollSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsManagerOrAbove()]

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


def pct_change(current, previous):
    if previous:
        return round((current - previous) / previous * 100, 2)
    return None


def highest_category(queryset, group_field='category', sum_field='amount'):
    """Return {name, amount} of the top category by summed amount."""
    aggregated = (
        queryset.values(f'{group_field}__name')
        .annotate(total=Sum(sum_field))
        .order_by('-total')
        .first()
    )
    if not aggregated:
        return None
    return {
        'name': aggregated[f'{group_field}__name'],
        'amount': float(aggregated['total']),
    }


def serialize_expense(expense):
    return {
        'source': 'finance_expense',
        'expense_id': expense.expense_id,
        'name': expense.name,
        'category': expense.category.name,
        'amount': float(expense.amount),
        'payment_method': expense.payment_method,
        'date': str(expense.date),
        'description': expense.description,
        'status': expense.status,
    }


def serialize_income(income):
    return {
        'source': 'finance_income',
        'income_id': income.income_id,
        'party_name': income.party_name,
        'category': income.category.name,
        'amount': float(income.amount),
        'payment_method': income.payment_method,
        'date': str(income.date),
        'status': income.status,
    }


def serialize_purchase(purchase):
    return {
        'source': 'purchase',
        'purchase_id': purchase.purchase_id,
        'vendor': purchase.vendor.name,
        'amount': float(purchase.total_amount),
        'payment_terms': purchase.payment_terms,
        'date': str(purchase.date),
        'status': purchase.status,
    }


def serialize_purchase_order(order):
    return {
        'source': 'purchase_order',
        'purchase_order_id': order.purchase_order_id,
        'vendor': order.vendor.name,
        'amount': float(order.total_amount),
        'payment_terms': order.payment_terms,
        'date': str(order.order_date),
        'status': order.status,
    }


def serialize_sales_order(order):
    return {
        'source': 'sales_order',
        'order_id': order.order_id,
        'customer': order.customer.name,
        'amount': float(order.total_amount),
        'payment_method': order.payment_method,
        'date': str(order.date),
        'status': order.status,
    }


def serialize_invoice(invoice):
    return {
        'source': 'invoice',
        'invoice_number': invoice.invoice_number,
        'customer_name': invoice.customer_name,
        'amount': float(invoice.total),
        'payment_method': invoice.payment_method,
        'date': str(invoice.invoice_date),
        'status': invoice.status,
    }


def top_vendor(purchases, orders=None):
    totals = {}
    for name, amount in purchases.values_list('vendor__name', 'total_amount'):
        totals[name] = totals.get(name, 0) + float(amount)
    if orders is not None:
        for name, amount in orders.values_list('vendor__name', 'total_amount'):
            totals[name] = totals.get(name, 0) + float(amount)
    if not totals:
        return None
    name = max(totals, key=totals.get)
    return {
        'name': name,
        'amount': totals[name],
    }


class ExpenseSummaryView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        result, error = parse_date_range(request)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        start, end = result

        expenses = Expense.objects.filter(
            date__gte=start, date__lte=end,
            status__in=['paid', 'approved'],
        )
        purchases = Purchase.objects.filter(
            date__gte=start, date__lte=end,
            status__in=['paid', 'partially_paid'],
        )
        orders = PurchaseOrder.objects.filter(
            order_date__gte=start, order_date__lte=end,
            status__in=['received', 'paid', 'partially_paid'],
        )
        category = request.query_params.get('category')
        status_filter = request.query_params.get('status')
        payment_method = request.query_params.get('payment_method')
        if category:
            expenses = expenses.filter(category=category)
        if status_filter:
            expenses = expenses.filter(status=status_filter)
            purchases = purchases.filter(status=status_filter)
            orders = orders.filter(status=status_filter)
        if payment_method:
            expenses = expenses.filter(payment_method=payment_method)

        finance_total = expenses.aggregate(total=Sum('amount'))['total'] or 0
        purchase_total = purchases.aggregate(total=Sum('total_amount'))['total'] or 0
        order_total = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        total_expense = float(finance_total) + float(purchase_total) + float(order_total)
        count = expenses.count() + purchases.count() + orders.count()

        expense_entries = [
            serialize_expense(e) for e in expenses.select_related('category')
        ]
        expense_entries.extend(
            serialize_purchase(p)
            for p in purchases.select_related('vendor')
        )
        expense_entries.extend(
            serialize_purchase_order(o)
            for o in orders.select_related('vendor')
        )

        return Response({
            'date_from': str(start),
            'date_to': str(end),
            'total_expense': total_expense,
            'finance_expense': float(finance_total),
            'purchase_expense': float(purchase_total) + float(order_total),
            'highest_category': highest_category(expenses),
            'top_vendor': top_vendor(purchases, orders),
            'average_expense': round(total_expense / count, 2) if count else 0,
            'sources': {
                'finance_expenses': {
                    'total': float(finance_total),
                    'count': expenses.count(),
                },
                'purchases': {
                    'total': float(purchase_total),
                    'count': purchases.count(),
                },
                'purchase_orders': {
                    'total': float(order_total),
                    'count': orders.count(),
                },
            },
            'expenses': expense_entries,
        }, status=status.HTTP_200_OK)


class IncomeSummaryView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        result, error = parse_date_range(request)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        start, end = result
        window_len = (end - start).days + 1
        prev_end = start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=window_len - 1)

        incomes = Income.objects.filter(
            date__gte=start, date__lte=end,
            status__in=['received', 'partial'],
        )
        sales_orders = SalesOrder.objects.filter(
            date__gte=start, date__lte=end,
            status='completed',
        )
        invoices = Invoice.objects.filter(
            invoice_date__gte=start, invoice_date__lte=end,
            status='paid',
        )
        category = request.query_params.get('category')
        status_filter = request.query_params.get('status')
        payment_method = request.query_params.get('payment_method')
        if category:
            incomes = incomes.filter(category=category)
        if status_filter:
            incomes = incomes.filter(status=status_filter)
            sales_orders = sales_orders.filter(status=status_filter)
            invoices = invoices.filter(status=status_filter)
        if payment_method:
            incomes = incomes.filter(payment_method=payment_method)
            sales_orders = sales_orders.filter(payment_method=payment_method)

        total_finance = incomes.aggregate(total=Sum('amount'))['total'] or 0
        total_sales = sales_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        total_invoice = invoices.aggregate(total=Sum('total'))['total'] or 0
        total_income = float(total_finance) + float(total_sales) + float(total_invoice)
        count = incomes.count() + sales_orders.count() + invoices.count()

        prev_finance = Income.objects.filter(
            date__gte=prev_start, date__lte=prev_end,
            status__in=['received', 'partial'],
        ).aggregate(total=Sum('amount'))['total'] or 0
        prev_sales = SalesOrder.objects.filter(
            date__gte=prev_start, date__lte=prev_end, status='completed',
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        prev_invoice = Invoice.objects.filter(
            invoice_date__gte=prev_start, invoice_date__lte=prev_end,
            status='paid',
        ).aggregate(total=Sum('total'))['total'] or 0
        prev_total = float(prev_finance) + float(prev_sales) + float(prev_invoice)

        sources = {
            'finance_incomes': {
                'total': float(total_finance),
                'count': incomes.count(),
            },
            'sales_orders': {
                'total': float(total_sales),
                'count': sales_orders.count(),
            },
            'invoices': {
                'total': float(total_invoice),
                'count': invoices.count(),
            },
        }
        top_source = (
            max(sources.items(), key=lambda kv: kv[1]['total'])[0]
            if total_income else None
        )

        income_entries = [
            serialize_income(i) for i in incomes.select_related('category')
        ]
        income_entries.extend(
            serialize_sales_order(o)
            for o in sales_orders.select_related('customer')
        )
        income_entries.extend(serialize_invoice(inv) for inv in invoices)

        return Response({
            'date_from': str(start),
            'date_to': str(end),
            'total_income': total_income,
            'finance_income': float(total_finance),
            'sales_income': float(total_sales),
            'invoice_income': float(total_invoice),
            'highest_category': highest_category(incomes),
            'top_source': top_source,
            'average_income': round(total_income / count, 2) if count else 0,
            'income_growth': pct_change(total_income, prev_total),
            'sources': sources,
            'incomes': income_entries,
        }, status=status.HTTP_200_OK)


class ProfitLossView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        result, error = parse_date_range(request)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        start, end = result

        finance_income = Income.objects.filter(
            date__gte=start, date__lte=end,
            status__in=['received', 'partial'],
        ).aggregate(total=Sum('amount'))['total'] or 0
        sales_income = SalesOrder.objects.filter(
            date__gte=start, date__lte=end, status='completed',
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        invoice_income = Invoice.objects.filter(
            invoice_date__gte=start, invoice_date__lte=end, status='paid',
        ).aggregate(total=Sum('total'))['total'] or 0
        total_revenue = (
            float(finance_income) + float(sales_income) + float(invoice_income)
        )

        finance_expense = Expense.objects.filter(
            date__gte=start, date__lte=end,
            status__in=['paid', 'approved'],
        ).aggregate(total=Sum('amount'))['total'] or 0
        purchase_expense = Purchase.objects.filter(
            date__gte=start, date__lte=end,
            status__in=['paid', 'partially_paid'],
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        total_expense = float(finance_expense) + float(purchase_expense)

        net_profit = total_revenue - total_expense
        margin = (
            round(net_profit / total_revenue * 100, 2)
            if total_revenue else None
        )

        return Response({
            'date_from': str(start),
            'date_to': str(end),
            'total_revenue': total_revenue,
            'total_expense': total_expense,
            'net_profit': net_profit,
            'margin_percent': margin,
            'revenue_sources': {
                'finance_incomes': float(finance_income),
                'sales_orders': float(sales_income),
                'invoices': float(invoice_income),
            },
            'expense_sources': {
                'finance_expenses': float(finance_expense),
                'purchases': float(purchase_expense),
            },
        }, status=status.HTTP_200_OK)


class IncomeVsExpenseView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        result, error = parse_date_range(request)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        start, end = result

        group_by = request.query_params.get('group_by', 'month')

        incomes = Income.objects.filter(
            date__gte=start, date__lte=end,
            status__in=['received', 'partial'],
        )
        sales_orders = SalesOrder.objects.filter(
            date__gte=start, date__lte=end, status='completed',
        )
        invoices = Invoice.objects.filter(
            invoice_date__gte=start, invoice_date__lte=end, status='paid',
        )
        expenses = Expense.objects.filter(
            date__gte=start, date__lte=end,
            status__in=['paid', 'approved'],
        )
        purchases = Purchase.objects.filter(
            date__gte=start, date__lte=end,
            status__in=['paid', 'partially_paid'],
        )

        total_finance_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
        total_sales_income = sales_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        total_invoice_income = invoices.aggregate(total=Sum('total'))['total'] or 0
        total_income = (
            float(total_finance_income)
            + float(total_sales_income)
            + float(total_invoice_income)
        )

        total_finance_expense = expenses.aggregate(total=Sum('amount'))['total'] or 0
        total_purchase_expense = purchases.aggregate(total=Sum('total_amount'))['total'] or 0
        total_expense = float(total_finance_expense) + float(total_purchase_expense)

        periods = []
        cursor = start
        while cursor <= end:
            if group_by == 'year':
                key = str(cursor.year)
                income = (
                    (incomes.filter(date__year=cursor.year).aggregate(
                        total=Sum('amount'),
                    )['total'] or 0)
                    + (sales_orders.filter(date__year=cursor.year).aggregate(
                        total=Sum('total_amount'),
                    )['total'] or 0)
                    + (invoices.filter(invoice_date__year=cursor.year).aggregate(
                        total=Sum('total'),
                    )['total'] or 0)
                )
                expense = (
                    (expenses.filter(date__year=cursor.year).aggregate(
                        total=Sum('amount'),
                    )['total'] or 0)
                    + (purchases.filter(date__year=cursor.year).aggregate(
                        total=Sum('total_amount'),
                    )['total'] or 0)
                )
                cursor = datetime(cursor.year + 1, 1, 1).date()
            else:
                key = cursor.strftime('%Y-%m')
                income = (
                    (incomes.filter(
                        date__year=cursor.year, date__month=cursor.month,
                    ).aggregate(total=Sum('amount'))['total'] or 0)
                    + (sales_orders.filter(
                        date__year=cursor.year, date__month=cursor.month,
                    ).aggregate(total=Sum('total_amount'))['total'] or 0)
                    + (invoices.filter(
                        invoice_date__year=cursor.year,
                        invoice_date__month=cursor.month,
                    ).aggregate(total=Sum('total'))['total'] or 0)
                )
                expense = (
                    (expenses.filter(
                        date__year=cursor.year, date__month=cursor.month,
                    ).aggregate(total=Sum('amount'))['total'] or 0)
                    + (purchases.filter(
                        date__year=cursor.year, date__month=cursor.month,
                    ).aggregate(total=Sum('total_amount'))['total'] or 0)
                )
                if cursor.month == 12:
                    cursor = datetime(cursor.year + 1, 1, 1).date()
                else:
                    cursor = datetime(cursor.year, cursor.month + 1, 1).date()

            difference = float(income) - float(expense)
            periods.append({
                'period': key,
                'income': float(income),
                'expense': float(expense),
                'difference': difference,
                'trend': '+' if difference >= 0 else '-',
            })

        net_difference = total_income - total_expense
        expense_ratio = (
            round(total_expense / total_income * 100, 2)
            if total_income else None
        )

        return Response({
            'date_from': str(start),
            'date_to': str(end),
            'group_by': group_by,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_difference': net_difference,
            'expense_ratio': expense_ratio,
            'sources': {
                'income': {
                    'finance_incomes': float(total_finance_income),
                    'sales_orders': float(total_sales_income),
                    'invoices': float(total_invoice_income),
                },
                'expense': {
                    'finance_expenses': float(total_finance_expense),
                    'purchases': float(total_purchase_expense),
                },
            },
            'periods': periods,
        }, status=status.HTTP_200_OK)


class TaxSummaryView(APIView):
    permission_classes = [IsManagerOrAbove]

    def get(self, request):
        result, error = parse_date_range(request)
        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        start, end = result
        window_len = (end - start).days + 1
        prev_end = start - timedelta(days=1)
        prev_start = prev_end - timedelta(days=window_len - 1)

        taxes = PurchaseTax.objects.filter(date__gte=start, date__lte=end)
        tax_type = request.query_params.get('tax_type')
        status_filter = request.query_params.get('status')
        supplier = request.query_params.get('supplier')
        if tax_type:
            taxes = taxes.filter(tax_type=tax_type)
        if status_filter:
            taxes = taxes.filter(status=status_filter)
        if supplier:
            taxes = taxes.filter(supplier__icontains=supplier)

        prev_taxes = PurchaseTax.objects.filter(
            date__gte=prev_start, date__lte=prev_end,
        )

        total_tax = taxes.aggregate(total=Sum('tax_amount'))['total'] or 0
        prev_total = prev_taxes.aggregate(total=Sum('tax_amount'))['total'] or 0
        count = taxes.count()

        sales_items = SalesOrderItem.objects.filter(
            order__date__gte=start, order__date__lte=end,
            order__status='completed',
        )
        sales_tax_total = sales_items.aggregate(total=Sum('tax_amount'))['total'] or 0

        paid_invoices = Invoice.objects.filter(
            invoice_date__gte=start, invoice_date__lte=end, status='paid',
        )
        invoice_tax_total = paid_invoices.aggregate(total=Sum('tax_amount'))['total'] or 0

        total_collected = float(sales_tax_total) + float(invoice_tax_total)
        total_paid = float(total_tax)
        net_tax = total_collected - total_paid

        breakdown = {}
        for row in sales_items.values('tax__name', 'tax__rate').annotate(
            total=Sum('tax_amount'),
        ):
            name = row['tax__name'] or 'Untaxed'
            entry = breakdown.setdefault(name, {
                'name': name, 'rate': row['tax__rate'],
                'collected': 0.0, 'paid': 0.0,
            })
            entry['collected'] += float(row['total'])
        for row in paid_invoices.values('tax__name', 'tax__rate').annotate(
            total=Sum('tax_amount'),
        ):
            name = row['tax__name'] or 'Untaxed'
            entry = breakdown.setdefault(name, {
                'name': name, 'rate': row['tax__rate'],
                'collected': 0.0, 'paid': 0.0,
            })
            entry['collected'] += float(row['total'])
        for row in taxes.values('tax_type__name', 'tax_type__rate').annotate(
            total=Sum('tax_amount'),
        ):
            name = row['tax_type__name'] or 'Untaxed'
            entry = breakdown.setdefault(name, {
                'name': name, 'rate': row['tax_type__rate'],
                'collected': 0.0, 'paid': 0.0,
            })
            entry['paid'] += float(row['total'])
        for entry in breakdown.values():
            entry['collected'] = round(entry['collected'], 2)
            entry['paid'] = round(entry['paid'], 2)
            entry['net'] = round(entry['collected'] - entry['paid'], 2)

        return Response({
            'date_from': str(start),
            'date_to': str(end),
            'total_purchase_tax': float(total_tax),
            'highest_tax_category': highest_category(taxes, 'tax_type', 'tax_amount'),
            'avg_tax_per_purchase': round(float(total_tax) / count, 2) if count else 0,
            'purchase_tax_growth': pct_change(float(total_tax), float(prev_total)),
            'total_collected_tax': total_collected,
            'total_sales_tax': float(sales_tax_total),
            'total_invoice_tax': float(invoice_tax_total),
            'net_tax': net_tax,
            'sources': {
                'purchase_taxes': {
                    'total': float(total_tax),
                    'count': count,
                },
                'sales_order_items': {
                    'total': float(sales_tax_total),
                    'count': sales_items.count(),
                },
                'invoices': {
                    'total': float(invoice_tax_total),
                    'count': paid_invoices.count(),
                },
            },
            'tax_breakdown': list(breakdown.values()),
            'taxes': [
                {
                    'bill_id': t.bill_id,
                    'supplier': t.supplier,
                    'tax_type': t.tax_type.name if t.tax_type else '',
                    'tax_amount': float(t.tax_amount),
                    'payment_method': t.payment_method,
                    'date': str(t.date),
                    'status': t.status,
                }
                for t in taxes.select_related('tax_type')
            ],
        }, status=status.HTTP_200_OK)
