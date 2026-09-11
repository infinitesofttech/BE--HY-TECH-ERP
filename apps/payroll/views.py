from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Sum

from .permissions import IsHROrAdmin, IsStaffOrAdmin
from .models import Payroll, Expense
from .serializers import PayrollSerializer, ExpenseSerializer
from apps.hytech_services.models import Transaction
from apps.hytech_services.serializers import TransactionSerializer


# PAYROLL


class PayrollListCreateAPIView(APIView):

    permission_classes = [IsHROrAdmin]

    def get(self, request):
        payrolls = Payroll.objects.select_related('employee').all()

        month = request.query_params.get('month')
        employee = request.query_params.get('employee')
        status_filter = request.query_params.get('status')

        if month:
            payrolls = payrolls.filter(payroll_month=month)
        if employee:
            payrolls = payrolls.filter(employee_id=employee)
        if status_filter:
            payrolls = payrolls.filter(status=status_filter)

        serializer = PayrollSerializer(payrolls, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PayrollSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Payroll created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PayrollSummaryAPIView(APIView):

    permission_classes = [IsHROrAdmin]

    def get(self, request):
        payrolls = Payroll.objects.all()

        month = request.query_params.get('month')
        if month:
            payrolls = payrolls.filter(payroll_month=month)

        gross_total = payrolls.aggregate(
            total=Sum('basic_pay') + Sum('hra') + Sum('allowances')
        )['total'] or 0
        statutory_deductions = payrolls.aggregate(
            total=Sum('pf')
        )['total'] or 0
        net_disbursed = payrolls.aggregate(
            total=Sum('net_monthly')
        )['total'] or 0

        return Response(
            {
                "gross_total_salary": float(gross_total),
                "total_statutory_deductions": float(statutory_deductions),
                "net_disbursed_to_bank": float(net_disbursed),
            },
            status=status.HTTP_200_OK,
        )


class PayrollDetailAPIView(APIView):

    permission_classes = [IsHROrAdmin]

    def get_object(self, pk):
        return get_object_or_404(
            Payroll.objects.select_related('employee'), pk=pk
        )

    def get(self, request, pk):
        payroll = self.get_object(pk)
        serializer = PayrollSerializer(payroll)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        payroll = self.get_object(pk)
        serializer = PayrollSerializer(payroll, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Payroll updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        payroll = self.get_object(pk)
        serializer = PayrollSerializer(payroll, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Payroll updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        payroll = self.get_object(pk)
        payroll_no = payroll.payroll_no
        payroll.delete()
        return Response(
            {"message": f"Payroll {payroll_no} deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class SalarySlipAPIView(APIView):

    permission_classes = [IsStaffOrAdmin]

    def get(self, request, pk):
        payroll = get_object_or_404(
            Payroll.objects.select_related('employee'), pk=pk
        )

        if not (request.user.is_staff or request.user.is_superuser
                or request.user.role in ('admin', 'hr')
                or payroll.employee_id == request.user.pk):
            return Response(
                {"error": "You are not authorized to view this salary slip."},
                status=status.HTTP_403_FORBIDDEN,
            )

        slip = {
            "payroll_no": payroll.payroll_no,
            "payroll_month": payroll.payroll_month,
            "employee_id": payroll.employee_id,
            "employee_name": payroll.employee.get_full_name() or payroll.employee.username,
            "employee_role": payroll.employee.role,
            "earnings": {
                "basic_pay": float(payroll.basic_pay),
                "hra": float(payroll.hra),
                "allowances": float(payroll.allowances),
                "total_earnings": float(
                    payroll.basic_pay + payroll.hra + payroll.allowances
                ),
            },
            "deductions": {
                "pf": float(payroll.pf),
                "total_deductions": float(payroll.pf),
            },
            "net_monthly": float(payroll.net_monthly),
            "status": payroll.status,
        }
        return Response(slip, status=status.HTTP_200_OK)


# EXPENSE


class ExpenseListCreateAPIView(APIView):

    permission_classes = [IsHROrAdmin]

    def get(self, request):
        expenses = Expense.objects.select_related('created_by').all()

        category = request.query_params.get('category')
        payment_mode = request.query_params.get('payment_mode')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        if category:
            expenses = expenses.filter(category=category)
        if payment_mode:
            expenses = expenses.filter(payment_mode=payment_mode)
        if date_from:
            expenses = expenses.filter(expense_date__gte=date_from)
        if date_to:
            expenses = expenses.filter(expense_date__lte=date_to)

        serializer = ExpenseSerializer(expenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            if getattr(request.user, 'role', None):
                serializer.save(created_by_id=request.user.pk)
            else:
                serializer.save()
            return Response(
                {
                    "message": "Expense created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpenseDetailAPIView(APIView):

    permission_classes = [IsHROrAdmin]

    def get_object(self, pk):
        return get_object_or_404(
            Expense.objects.select_related('created_by'), pk=pk
        )

    def get(self, request, pk):
        expense = self.get_object(pk)
        serializer = ExpenseSerializer(expense)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        expense = self.get_object(pk)
        serializer = ExpenseSerializer(expense, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Expense updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        expense = self.get_object(pk)
        serializer = ExpenseSerializer(expense, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Expense updated successfully.", "data": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        expense = self.get_object(pk)
        expense_no = expense.expense_no
        expense.delete()
        return Response(
            {"message": f"Expense {expense_no} deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


# FINANCE SUMMARY & HISTORY


def apply_period_filter(qs, date_field, request):
    month = request.query_params.get('month')
    year = request.query_params.get('year')
    if month:
        qs = qs.filter(**{f'{date_field}__month': month})
    if year:
        qs = qs.filter(**{f'{date_field}__year': year})
    return qs


class FinanceSummaryAPIView(APIView):

    permission_classes = [IsHROrAdmin]

    def get(self, request):
        transactions = apply_period_filter(
            Transaction.objects.all(), 'transaction_date', request
        )
        expenses = apply_period_filter(Expense.objects.all(), 'expense_date', request)

        total_income = transactions.aggregate(
            total=Sum('bill_amount')
        )['total'] or 0
        total_expense = expenses.aggregate(
            total=Sum('amount')
        )['total'] or 0

        return Response(
            {
                "total_income": float(total_income),
                "total_expense": float(total_expense),
                "gross_profit": float(total_income - total_expense),
            },
            status=status.HTTP_200_OK,
        )


class IncomeHistoryAPIView(APIView):

    permission_classes = [IsHROrAdmin]

    def get(self, request):
        transactions = Transaction.objects.select_related(
            'customer', 'service', 'sub_service', 'staff'
        )
        transactions = apply_period_filter(
            transactions, 'transaction_date', request
        ).order_by('-transaction_date')

        serializer = TransactionSerializer(transactions, many=True)
        return Response(
            {"history": serializer.data},
            status=status.HTTP_200_OK,
        )


class ExpenseHistoryAPIView(APIView):

    permission_classes = [IsHROrAdmin]

    def get(self, request):
        expenses = Expense.objects.select_related('created_by')
        expenses = apply_period_filter(expenses, 'expense_date', request)

        serializer = ExpenseSerializer(expenses, many=True)
        return Response(
            {"history": serializer.data},
            status=status.HTTP_200_OK,
        )


class AllHistoryAPIView(APIView):

    permission_classes = [IsHROrAdmin]

    def get(self, request):
        transactions = Transaction.objects.select_related(
            'customer', 'service', 'sub_service', 'staff'
        )
        transactions = apply_period_filter(
            transactions, 'transaction_date', request
        ).order_by('-transaction_date')

        expenses = Expense.objects.select_related('created_by')
        expenses = apply_period_filter(expenses, 'expense_date', request)

        income = []
        for obj in transactions:
            income.append({
                "type": "income",
                "reference_no": obj.transaction_no,
                "date": str(obj.transaction_date),
                "title": obj.customer.head_of_family if obj.customer else '',
                "amount": float(obj.bill_amount),
                "payment_mode": obj.payment_mode,
            })

        expense_history = []
        for obj in expenses:
            expense_history.append({
                "type": "expense",
                "reference_no": obj.expense_no,
                "date": str(obj.expense_date) if obj.expense_date else None,
                "title": obj.expense_name,
                "amount": float(obj.amount),
                "payment_mode": obj.payment_mode,
                "category": obj.get_category_display(),
            })

        combined = income + expense_history
        combined.sort(key=lambda x: x.get('date') or '', reverse=True)

        return Response(
            {
                "all_history": combined,
            },
            status=status.HTTP_200_OK,
        )
