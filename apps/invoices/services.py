from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from .models import Invoice, InvoiceItem, Payment


def create_invoice_from_delivery_note(delivery_note, employee=None,
                                      due_in_days=15):
    """Raise an invoice from a dispatched delivery note."""
    existing = delivery_note.invoices.first()
    if existing:
        return existing

    with transaction.atomic():
        invoice = Invoice.objects.create(
            sales_order=delivery_note.sales_order,
            delivery_note=delivery_note,
            customer_name=delivery_note.customer.name,
            customer_email=delivery_note.customer.email,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=due_in_days),
            tax=delivery_note.tax,
            status='sent',
            created_by=employee,
        )
        item_objs = []
        for item in delivery_note.items.select_related('product').all():
            item_objs.append(InvoiceItem(
                invoice=invoice,
                description=item.product.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total=item.amount,
            ))
        InvoiceItem.objects.bulk_create(item_objs)

        subtotal = delivery_note.items.aggregate(total=Sum('amount'))['total'] or 0
        invoice.subtotal = subtotal
        invoice.tax_amount = subtotal * (
            delivery_note.tax_percentage / Decimal('100')
        )
        invoice.discount_amount = delivery_note.total_discount
        invoice.total = delivery_note.total_amount
        invoice.save(update_fields=[
            'subtotal', 'tax_amount', 'discount_amount', 'total',
        ])
    return invoice


def mark_invoice_paid(invoice, method='cash', amount=None, payment_date=None,
                      reference_number='', notes=''):
    """Record a payment against an invoice and mark it paid."""
    amount = amount or invoice.total
    with transaction.atomic():
        Payment.objects.create(
            invoice=invoice,
            amount=amount,
            method=method,
            payment_date=payment_date or date.today(),
            reference_number=reference_number,
            notes=notes,
        )
        invoice.status = 'paid'
        invoice.transaction_id = reference_number or invoice.transaction_id
        invoice.save(update_fields=['status', 'transaction_id', 'updated_at'])
    return invoice
