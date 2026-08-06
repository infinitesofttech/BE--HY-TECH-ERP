from datetime import date
from decimal import Decimal

from django.db import transaction

from apps.sales.models import Customer, SalesOrder, SalesOrderItem


def create_sales_order_from_quotation(quotation, employee=None):
    """Convert an accepted quotation into a SalesOrder and mark the lead won."""
    customer = quotation.customer
    if customer is None:
        lead = quotation.lead
        customer, _ = Customer.objects.get_or_create(
            name=quotation.client or (lead.name if lead else 'Walk-in Customer'),
            defaults={
                'email': lead.email if lead else '',
                'phone': lead.phone if lead else '',
            },
        )
        quotation.customer = customer
        quotation.save(update_fields=['customer'])

    with transaction.atomic():
        sales_order = SalesOrder.objects.create(
            employee=employee,
            quotation=quotation,
            customer=customer,
            date=date.today(),
            status='in_progress',
        )
        item_objs = []
        for item in quotation.items.select_related('product').all():
            if item.product is None:
                continue
            quantity = item.quantity
            unit_price = item.price
            discount = (quantity * unit_price) - item.amount
            tax_rate = quotation.tax_percentage
            amount = (quantity * unit_price) - discount
            tax_amount = amount * tax_rate / Decimal('100')
            item_objs.append(SalesOrderItem(
                order=sales_order,
                product=item.product,
                quantity=quantity,
                unit_price=unit_price,
                discount=discount,
                tax=quotation.tax,
                amount=amount,
                tax_amount=tax_amount,
            ))
        SalesOrderItem.objects.bulk_create(item_objs)
        sales_order.recalculate_total()

    if quotation.lead:
        quotation.lead.status = 'won'
        quotation.lead.save(update_fields=['status', 'updated_at'])

    return sales_order


def approve_quotation(quotation, employee=None):
    if quotation.status == 'accepted':
        return quotation.sales_orders.first()
    quotation.status = 'accepted'
    quotation.save(update_fields=['status', 'updated_at'])
    return create_sales_order_from_quotation(quotation, employee=employee)


def reject_quotation(quotation, lost_reason=''):
    quotation.status = 'rejected'
    quotation.save(update_fields=['status', 'updated_at'])
    if quotation.lead and quotation.lead.status not in ('won', 'lost'):
        quotation.lead.status = 'lost'
        quotation.lead.reviews = lost_reason or quotation.lead.reviews
        quotation.lead.save(update_fields=['status', 'reviews', 'updated_at'])
    return quotation


def send_quotation(quotation):
    if quotation.status in ('draft', 'expired'):
        quotation.status = 'sent'
        quotation.save(update_fields=['status', 'updated_at'])
    return quotation
