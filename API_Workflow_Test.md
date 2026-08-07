# CRM System - Full Manufacturing Workflow API Test Guide

End-to-end sequence that turns an enquiry into an **invoice payment**, driving the
entire document chain automatically: **Lead -> Quotation -> Sales Order -> Job Order ->
Requisition -> Purchase Order -> GRN -> QC -> Material Issue -> Production -> Finished
Goods -> Dispatch -> Delivery Note -> Invoice -> Payment**.

Every request and response below was **captured from a real API run** against this
project (all 32 calls returned 200/201). Auto-generated numbers (e.g. `QOT0014`, `SO-0040`,
`JO-0012`, `PRQ-0011`, `PO-0015`, `GRN-0009`, `QI-0009`, `MIS-0006`, `FG-0004`, `DS-0004`,
`DN-0012`, `INV-0007`) are **sequential and will differ on your machine** - always read the
ids/numbers from the response of the previous step.

---

## Prerequisites

### 1. Seed / reference data already in the database

| Id | What | Notes |
|----|------|-------|
| 29 | **Steel Cabinet** | finished good, price 800.00, unit `piece` |
| 27 | **Steel Sheet** | raw material, cost price 100.00 |
| 28 | **Pipe** | raw material, cost price 40.00 |
| 1 | **Cabinet BOM** | 4 x Steel Sheet + 2 m Pipe per Steel Cabinet, active |
| 18 | **Main Store** | warehouse used for raw material stock |
| 1 | **CNC Cutting Machine** | machine code M-001 |
| 4 | **GST** | tax 18% |
| 5 | **Acme Auto Parts** | active vendor used for the auto-created PO |

> The scenario below manufactures **1 x Steel Cabinet**. Starting stock is set to
> **Steel Sheet = 2, Pipe = 30** so the material check reports a shortfall that must be
> bought in through a requisition -> PO -> GRN.

### 2. Create an admin test user (once)

```powershell
python manage.py shell -c "from django.contrib.auth import get_user_model; u=get_user_model().objects.create_user(email=`apitester@crm.local`, username=`apitester`, password=`Test@12345`, role=`super_admin`)"
```

### 3. Reset the raw-material stock to the known baseline (optional, for a deterministic run)

```powershell
python manage.py shell -c "from apps.products.models import Inventory; Inventory.objects.filter(warehouse_id=18, product_id=27).update(quantity=2); Inventory.objects.filter(warehouse_id=18, product_id=28).update(quantity=30)"
```

---

## Flow overview

```
POST /api/auth/login/
   |
   v
POST /api/pipeline/leads/ ........................................ create Lead
   |
   v
POST /api/orders/quotations/ .................................... create Quotation (with lead)
POST /api/orders/quotations/{id}/send/ .......................... status: sent
POST /api/orders/quotations/{id}/approve/ ....................... -> auto SalesOrder + Lead=won
   |
   v
POST /api/sales/orders/{id}/start-production/ ................... -> auto JobOrder
   |
   v
POST /api/production/job-orders/{id}/check-stock/ ................ Steel Sheet SHORT
POST /api/production/job-orders/{id}/create-requisition/ ......... -> PurchaseRequisition
POST /api/production/requisitions/{id}/approve/ .................. -> auto PurchaseOrder
POST /api/production/grns/ ...................................... create GRN for the PO
POST /api/production/grns/{id}/receive/ ......................... + stock in Main Store
POST /api/production/grns/{id}/inspect/ ......................... -> auto QualityInspection
POST /api/production/inspections/{id}/result/ ................... GRN accepted
POST /api/production/job-orders/{id}/check-stock/ ................ now AVAILABLE
POST /api/production/job-orders/{id}/issue-material/ ............. -> MaterialIssueSlip, stock consumed
   |
   v
POST /api/production/job-orders/{id}/start/ ..................... creates 8 processes
POST /api/production/processes/{id}/advance/ (x8) ............... cutting -> fabrication -> machining
                                                     welding -> grinding -> painting -> assembly -> qc
POST /api/production/job-orders/{id}/qc/ ........................ -> FinishedGoods
   |
   v
POST /api/production/job-orders/{id}/dispatch/ .................. -> Dispatch + auto DeliveryNote
POST /api/production/dispatches/{id}/mark-dispatched/ ............ status: dispatched
   |
   v
POST /api/sales/delivery-notes/{id}/create-invoice/ .............. -> Invoice
POST /api/invoices/invoices/{id}/mark-paid/ ...................... -> Payment + Invoice=paid
```

---

## Step 1: Login

**`POST http://localhost:8000/api/auth/login/`**

**Headers**

```
Content-Type: application/json
```

**Request body**

```json
{
  "email": "apitester@crm.local",
  "password": "Test@12345"
}
```

**Response - HTTP 200**

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ...(truncated)",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ...(truncated)",
  "user": {
    "id": 23,
    "email": "apitester@crm.local",
    "first_name": "",
    "last_name": "",
    "username": "apitester",
    "role": "super_admin",
    "phone": "",
    "avatar": null,
    "territory": "",
    "pin_code": "",
    "manager": null,
    "manager_name": null,
    "device_token": "",
    "address": "",
    "city": "",
    "state": "",
    "date_of_birth": null,
    "joining_date": null,
    "department": null,
    "department_name": "",
    "designation": null,
    "designation_name": "",
    "shift_start_time": null,
    "shift_end_time": null,
    "salary": "0.00",
    "is_active": true,
    "date_joined": "2026-08-06T12:40:27.723701+05:30"
  }
}
```

---

## Step 2: Create Lead

**`POST http://localhost:8000/api/pipeline/leads/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{
  "first_name": "Demo",
  "last_name": "Customer",
  "lead_type": "organization",
  "company_name": "Acme Corp Test",
  "email": "acme.test@example.com",
  "phone": "9876543210",
  "value": "800.00",
  "product_requirement": "Steel Cabinet",
  "quantity": 1,
  "status": "new",
  "visibility": "public"
}
```

**Response - HTTP 201**

```json
{
  "id": 16,
  "owner_name": "",
  "name": "Demo Customer",
  "visible_to_names": [],
  "first_name": "Demo",
  "last_name": "Customer",
  "lead_type": "organization",
  "company_name": "Acme Corp Test",
  "email": "acme.test@example.com",
  "email_opt_out": false,
  "phone": "9876543210",
  "phone_2": "",
  "fax": "",
  "website": "",
  "value": "800.00",
  "product_requirement": "Steel Cabinet",
  "quantity": 1,
  "reviews": "",
  "avatar": null,
  "language": "English",
  "status": "new",
  "tags": "",
  "description": "",
  "visibility": "public",
  "street_address": "",
  "city": "",
  "state": "",
  "country": "",
  "zipcode": "",
  "facebook": "",
  "skype": "",
  "linkedin": "",
  "twitter": "",
  "whatsapp": "",
  "instagram": "",
  "created_at": "2026-08-06T12:47:17.960209+05:30",
  "updated_at": "2026-08-06T12:47:17.960209+05:30",
  "owner": null,
  "source": null,
  "industry": null,
  "contacts": [],
  "visible_to": []
}
```

---

## Step 3: Create Quotation

**`POST http://localhost:8000/api/orders/quotations/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{
  "client": "Acme Corp Test",
  "lead": 16,
  "quote_date": "2026-08-06",
  "valid_till": "2026-09-05",
  "payment_terms": "net_30",
  "tax": 4,
  "discount": 0,
  "status": "draft",
  "items": [
    {
      "product": 29,
      "quantity": 1,
      "price": "800.00",
      "discount": 0
    }
  ]
}
```

**Response - HTTP 201**

```json
{
  "id": 14,
  "quote_id": "QOT0014",
  "client": "Acme Corp Test",
  "lead": 16,
  "lead_name": "Demo Customer",
  "customer": null,
  "customer_name": "",
  "quote_date": "2026-08-06",
  "valid_till": "2026-09-05",
  "delivery_date": null,
  "payment_terms": "net_30",
  "tax": 4,
  "tax_name": "GST",
  "tax_percentage": "18.00",
  "gst_amount": "144.00",
  "shipping_charge": "0.00",
  "total_amount": "800.00",
  "discount": "0.00",
  "final_amount": "944.00",
  "notes": "",
  "status": "draft",
  "created_by": 23,
  "created_by_name": "apitester@crm.local",
  "items": [
    {
      "id": 14,
      "product": 29,
      "product_name": "Steel Cabinet",
      "quantity": 1,
      "price": "800.00",
      "discount": "0.00",
      "amount": "800.00"
    }
  ],
  "created_at": "2026-08-06T12:47:18.038212+05:30",
  "updated_at": "2026-08-06T12:47:18.038212+05:30"
}
```

---

## Step 4: Send Quotation

**`POST http://localhost:8000/api/orders/quotations/14/send/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 200**

```json
{
  "id": 14,
  "quote_id": "QOT0014",
  "client": "Acme Corp Test",
  "lead": 16,
  "lead_name": "Demo Customer",
  "customer": null,
  "customer_name": "",
  "quote_date": "2026-08-06",
  "valid_till": "2026-09-05",
  "delivery_date": null,
  "payment_terms": "net_30",
  "tax": 4,
  "tax_name": "GST",
  "tax_percentage": "18.00",
  "gst_amount": "144.00",
  "shipping_charge": "0.00",
  "total_amount": "800.00",
  "discount": "0.00",
  "final_amount": "944.00",
  "notes": "",
  "status": "sent",
  "created_by": 23,
  "created_by_name": "apitester@crm.local",
  "items": [
    {
      "id": 14,
      "product": 29,
      "product_name": "Steel Cabinet",
      "quantity": 1,
      "price": "800.00",
      "discount": "0.00",
      "amount": "800.00"
    }
  ],
  "created_at": "2026-08-06T12:47:18.038212+05:30",
  "updated_at": "2026-08-06T12:47:18.067205+05:30"
}
```

---

## Step 5: Approve Quotation

**`POST http://localhost:8000/api/orders/quotations/14/approve/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 201**

```json
{
  "quotation": {
    "id": 14,
    "quote_id": "QOT0014",
    "client": "Acme Corp Test",
    "lead": 16,
    "lead_name": "Demo Customer",
    "customer": 18,
    "customer_name": "Acme Corp Test",
    "quote_date": "2026-08-06",
    "valid_till": "2026-09-05",
    "delivery_date": null,
    "payment_terms": "net_30",
    "tax": 4,
    "tax_name": "GST",
    "tax_percentage": "18.00",
    "gst_amount": "144.00",
    "shipping_charge": "0.00",
    "total_amount": "800.00",
    "discount": "0.00",
    "final_amount": "944.00",
    "notes": "",
    "status": "accepted",
    "created_by": 23,
    "created_by_name": "apitester@crm.local",
    "items": [
      {
        "id": 14,
        "product": 29,
        "product_name": "Steel Cabinet",
        "quantity": 1,
        "price": "800.00",
        "discount": "0.00",
        "amount": "800.00"
      }
    ],
    "created_at": "2026-08-06T12:47:18.038212+05:30",
    "updated_at": "2026-08-06T12:47:18.089206+05:30"
  },
  "sales_order": {
    "id": 40,
    "order_id": "SO-0040",
    "quotation": 14,
    "quotation_id_ref": "QOT0014",
    "employee": 23,
    "employee_name": "apitester@crm.local",
    "customer": 18,
    "customer_name": "Acme Corp Test",
    "company_logo": null,
    "company_from": "",
    "company_to": "",
    "date": "2026-08-06",
    "payment_method": "cash",
    "status": "in_progress",
    "total_discount": "0.00",
    "shipping_charge": "0.00",
    "total_amount": "944.00",
    "notes": "",
    "terms_conditions": "",
    "items": [
      {
        "id": 45,
        "product": 29,
        "product_name": "Steel Cabinet",
        "quantity": 1,
        "unit_price": "800.00",
        "discount": "0.00",
        "amount": "800.00",
        "tax": 4,
        "tax_name": "GST",
        "tax_percentage": "18.00",
        "tax_amount": "144.00"
      }
    ],
    "created_at": "2026-08-06T12:47:18.097206+05:30",
    "updated_at": "2026-08-06T12:47:18.097206+05:30"
  }
}
```

---

## Step 6: Start Production

**`POST http://localhost:8000/api/sales/orders/40/start-production/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{
  "start_date": "2026-08-06"
}
```

**Response - HTTP 201**

```json
{
  "sales_order_id": "SO-0040",
  "job_orders": [
    {
      "id": 12,
      "job_no": "JO-0012",
      "sales_order": 40,
      "sales_order_id_ref": "SO-0040",
      "quotation": 14,
      "customer": 18,
      "customer_name": "Acme Corp Test",
      "product": 29,
      "product_name": "Steel Cabinet",
      "quantity": 1,
      "start_date": "2026-08-06",
      "end_date": null,
      "priority": "medium",
      "status": "planned",
      "status_display": "Planned",
      "progress": 0,
      "machine": null,
      "machine_name": "",
      "supervisor": null,
      "supervisor_name": null,
      "operators": [],
      "bom": 1,
      "bom_name": "Cabinet BOM",
      "notes": "",
      "material_requirements": [],
      "processes": [],
      "finished_goods": [],
      "created_at": "2026-08-06T12:47:18.268208+05:30",
      "updated_at": "2026-08-06T12:47:18.268208+05:30"
    }
  ]
}
```

---

## Step 7: Check Stock (short)

**`POST http://localhost:8000/api/production/job-orders/12/check-stock/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 200**

```json
{
  "job_order": {
    "id": 12,
    "job_no": "JO-0012",
    "sales_order": 40,
    "sales_order_id_ref": "SO-0040",
    "quotation": 14,
    "customer": 18,
    "customer_name": "Acme Corp Test",
    "product": 29,
    "product_name": "Steel Cabinet",
    "quantity": 1,
    "start_date": "2026-08-06",
    "end_date": null,
    "priority": "medium",
    "status": "waiting_material",
    "status_display": "Waiting for Material",
    "progress": 0,
    "machine": null,
    "machine_name": "",
    "supervisor": null,
    "supervisor_name": null,
    "operators": [],
    "bom": 1,
    "bom_name": "Cabinet BOM",
    "notes": "",
    "material_requirements": [
      {
        "id": 23,
        "raw_material": 27,
        "raw_material_name": "Steel Sheet",
        "required_quantity": "4.00",
        "available_quantity": "2.00",
        "issued_quantity": "0.00",
        "status": "short",
        "updated_at": "2026-08-06T12:47:18.330211+05:30"
      },
      {
        "id": 24,
        "raw_material": 28,
        "raw_material_name": "Pipe",
        "required_quantity": "2.00",
        "available_quantity": "30.00",
        "issued_quantity": "0.00",
        "status": "available",
        "updated_at": "2026-08-06T12:47:18.336210+05:30"
      }
    ],
    "processes": [],
    "finished_goods": [],
    "created_at": "2026-08-06T12:47:18.268208+05:30",
    "updated_at": "2026-08-06T12:47:18.338210+05:30"
  },
  "requirements": [
    {
      "raw_material": "Steel Sheet",
      "required_quantity": 4.0,
      "available_quantity": 2.0,
      "status": "short"
    },
    {
      "raw_material": "Pipe",
      "required_quantity": 2.0,
      "available_quantity": 30.0,
      "status": "available"
    }
  ]
}
```

---

## Step 8: Create Requisition

**`POST http://localhost:8000/api/production/job-orders/12/create-requisition/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{
  "department": "Production"
}
```

**Response - HTTP 201**

```json
{
  "id": 11,
  "requisition_no": "PRQ-0011",
  "job_order": 12,
  "job_no": "JO-0012",
  "department": "Production",
  "requested_by": 23,
  "requested_by_name": "apitester@crm.local",
  "approved_by": null,
  "approved_by_name": null,
  "status": "pending",
  "status_display": "Pending",
  "approval_date": null,
  "items": [
    {
      "id": 11,
      "raw_material": 27,
      "raw_material_name": "Steel Sheet",
      "quantity": "2.00",
      "required_date": null
    }
  ],
  "created_at": "2026-08-06T12:47:18.394209+05:30",
  "updated_at": "2026-08-06T12:47:18.394209+05:30"
}
```

---

## Step 9: Approve Requisition

**`POST http://localhost:8000/api/production/requisitions/11/approve/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 200**

```json
{
  "requisition": {
    "id": 11,
    "requisition_no": "PRQ-0011",
    "job_order": 12,
    "job_no": "JO-0012",
    "department": "Production",
    "requested_by": 23,
    "requested_by_name": "apitester@crm.local",
    "approved_by": 23,
    "approved_by_name": "apitester@crm.local",
    "status": "po_created",
    "status_display": "PO Created",
    "approval_date": "2026-08-06",
    "items": [
      {
        "id": 11,
        "raw_material": 27,
        "raw_material_name": "Steel Sheet",
        "quantity": "2.00",
        "required_date": null
      }
    ],
    "created_at": "2026-08-06T12:47:18.394209+05:30",
    "updated_at": "2026-08-06T12:47:18.421207+05:30"
  },
  "purchase_order_id": "PO-0015"
}
```

---

## Step 10: List Purchase Orders

**`GET http://localhost:8000/api/purchases/purchase-orders/`**

**Headers**

```
Authorization: Bearer <access_token>
```

**Response - HTTP 200**

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 15,
      "purchase_order_id": "PO-0015",
      "vendor": 5,
      "vendor_name": "Acme Auto Parts",
      "company_logo": null,
      "company_from": "",
      "company_to": "",
      "reference": "Requisition PRQ-0011",
      "order_date": "2026-08-06",
      "expected_delivery_date": null,
      "actual_delivery_date": null,
      "lead_time_days": null,
      "on_time": null,
      "payment_terms": "net_30",
      "status": "pending",
      "tax": null,
      "tax_percentage": "0.00",
      "total_discount": "0.00",
      "shipping_charge": "0.00",
      "total_amount": "200.00",
      "notes": "",
      "terms_conditions": "",
      "items": [
        {
          "id": 15,
          "product": 27,
          "product_name": "Steel Sheet",
          "quantity": 2,
          "unit_price": "100.00",
          "discount": "0.00",
          "amount": "200.00",
          "note": ""
        }
      ],
      "created_at": "2026-08-06T12:47:18.427208+05:30",
      "updated_at": "2026-08-06T12:47:18.427208+05:30"
    },
    {
      "id": 9,
      "purchase_order_id": "PO-0009",
      "vendor": 5,
      "vendor_name": "Acme Auto Parts",
      "company_logo": null,
      "company_from": "",
      "company_to": "",
      "reference": "Requisition PRQ-0005",
      "order_date": "2026-08-06",
      "expected_delivery_date": null,
      "actual_delivery_date": null,
      "lead_time_days": null,
      "on_time": null,
      "payment_terms": "net_30",
      "status": "pending",
      "tax": null,
      "tax_percentage": "0.00",
      "total_discount": "0.00",
      "shipping_charge": "0.00",
      "total_amount": "600.00",
      "notes": "",
      "terms_conditions": "",
      "items": [
        {
          "id": 9,
          "product": 27,
          "product_name": "Steel Sheet",
          "quantity": 6,
          "unit_price": "100.00",
          "discount": "0.00",
          "amount": "600.00",
          "note": ""
        }
      ],
      "created_at": "2026-08-06T12:17:01.854228+05:30",
      "updated_at": "2026-08-06T12:17:01.854228+05:30"
    },
    {
      "id": 4,
      "purchase_order_id": "PO-0004",
      "vendor": 5,
      "vendor_name": "Acme Auto Parts",
      "company_logo": null,
      "company_from": "Company HQ, Street 1",
      "company_to": "Acme Auto Parts, Street 2",
      "reference": "PO-REF-001",
      "order_date": "2026-08-01",
      "expected_delivery_date": "2026-08-10",
      "actual_delivery_date": null,
      "lead_time_days": 9,
      "on_time": null,
      "payment_terms": "net_30",
      "status": "pending",
      "tax": 8,
      "tax_name": "Tax 10.00%",
      "tax_percentage": "10.00",
      "total_discount": "5.00",
      "shipping_charge": "10.00",
      "total_amount": "214.00",
      "notes": "Please arrange delivery",
      "terms_conditions": "Standard terms apply",
      "items": [
        {
          "id": 4,
          "product": 1,
          "product_name": "Synthetic Oil 5W30",
          "quantity": 2,
          "unit_price": "100.00",
          "discount": "10.00",
          "amount": "190.00",
          "note": ""
        }
      ],
      "created_at": "2026-08-04T15:47:00.503815+05:30",
      "updated_at": "2026-08-04T15:49:14.062778+05:30"
    }
  ]
}
```

---

## Step 11: Create GRN

**`POST http://localhost:8000/api/production/grns/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{
  "purchase_order": 15,
  "supplier": 5,
  "warehouse": 18,
  "received_date": "2026-08-06",
  "status": "received",
  "received_by": 23,
  "notes": "Received per PO",
  "items": [
    {
      "product": 27,
      "quantity": 2
    }
  ]
}
```

**Response - HTTP 201**

```json
{
  "id": 9,
  "grn_no": "GRN-0009",
  "purchase_order": 15,
  "purchase_order_id_ref": "PO-0015",
  "supplier": 5,
  "supplier_name": "Acme Auto Parts",
  "warehouse": 18,
  "warehouse_name": "Main Store",
  "received_date": "2026-08-06",
  "status": "received",
  "status_display": "Received",
  "received_by": 23,
  "received_by_name": "apitester@crm.local",
  "notes": "Received per PO",
  "items": [
    {
      "id": 9,
      "product": 27,
      "product_name": "Steel Sheet",
      "quantity": "2.00",
      "accepted_quantity": "0.00",
      "rejected_quantity": "0.00",
      "rejection_reason": ""
    }
  ],
  "created_at": "2026-08-06T12:47:18.499206+05:30",
  "updated_at": "2026-08-06T12:47:18.499206+05:30"
}
```

---

## Step 12: Receive GRN

**`POST http://localhost:8000/api/production/grns/9/receive/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 200**

```json
{
  "id": 9,
  "grn_no": "GRN-0009",
  "purchase_order": 15,
  "purchase_order_id_ref": "PO-0015",
  "supplier": 5,
  "supplier_name": "Acme Auto Parts",
  "warehouse": 18,
  "warehouse_name": "Main Store",
  "received_date": "2026-08-06",
  "status": "received",
  "status_display": "Received",
  "received_by": 23,
  "received_by_name": "apitester@crm.local",
  "notes": "Received per PO",
  "items": [
    {
      "id": 9,
      "product": 27,
      "product_name": "Steel Sheet",
      "quantity": "2.00",
      "accepted_quantity": "2.00",
      "rejected_quantity": "0.00",
      "rejection_reason": ""
    }
  ],
  "created_at": "2026-08-06T12:47:18.499206+05:30",
  "updated_at": "2026-08-06T12:47:18.538206+05:30"
}
```

---

## Step 13: Inspect GRN

**`POST http://localhost:8000/api/production/grns/9/inspect/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 201**

```json
{
  "id": 9,
  "inspection_no": "QI-0009",
  "grn": 9,
  "grn_no": "GRN-0009",
  "job_order": null,
  "job_no": "",
  "product": null,
  "product_name": "",
  "quantity": "0.00",
  "status": "pending",
  "status_display": "Pending",
  "inspected_by": null,
  "inspected_by_name": null,
  "inspection_date": null,
  "notes": "",
  "created_at": "2026-08-06T12:47:18.571211+05:30",
  "updated_at": "2026-08-06T12:47:18.571211+05:30"
}
```

---

## Step 14: Inspection Result

**`POST http://localhost:8000/api/production/inspections/9/result/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{
  "passed": true,
  "notes": "Sample passed"
}
```

**Response - HTTP 200**

```json
{
  "id": 9,
  "inspection_no": "QI-0009",
  "grn": 9,
  "grn_no": "GRN-0009",
  "job_order": null,
  "job_no": "",
  "product": null,
  "product_name": "",
  "quantity": "0.00",
  "status": "passed",
  "status_display": "Passed",
  "inspected_by": 23,
  "inspected_by_name": "apitester@crm.local",
  "inspection_date": "2026-08-06",
  "notes": "Sample passed",
  "created_at": "2026-08-06T12:47:18.571211+05:30",
  "updated_at": "2026-08-06T12:47:18.590207+05:30"
}
```

---

## Step 15: Check Stock (available)

**`POST http://localhost:8000/api/production/job-orders/12/check-stock/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 200**

```json
{
  "job_order": {
    "id": 12,
    "job_no": "JO-0012",
    "sales_order": 40,
    "sales_order_id_ref": "SO-0040",
    "quotation": 14,
    "customer": 18,
    "customer_name": "Acme Corp Test",
    "product": 29,
    "product_name": "Steel Cabinet",
    "quantity": 1,
    "start_date": "2026-08-06",
    "end_date": null,
    "priority": "medium",
    "status": "material_ready",
    "status_display": "Material Ready",
    "progress": 0,
    "machine": null,
    "machine_name": "",
    "supervisor": null,
    "supervisor_name": null,
    "operators": [],
    "bom": 1,
    "bom_name": "Cabinet BOM",
    "notes": "",
    "material_requirements": [
      {
        "id": 23,
        "raw_material": 27,
        "raw_material_name": "Steel Sheet",
        "required_quantity": "4.00",
        "available_quantity": "4.00",
        "issued_quantity": "0.00",
        "status": "available",
        "updated_at": "2026-08-06T12:47:18.619223+05:30"
      },
      {
        "id": 24,
        "raw_material": 28,
        "raw_material_name": "Pipe",
        "required_quantity": "2.00",
        "available_quantity": "30.00",
        "issued_quantity": "0.00",
        "status": "available",
        "updated_at": "2026-08-06T12:47:18.627210+05:30"
      }
    ],
    "processes": [],
    "finished_goods": [],
    "created_at": "2026-08-06T12:47:18.268208+05:30",
    "updated_at": "2026-08-06T12:47:18.629207+05:30"
  },
  "requirements": [
    {
      "raw_material": "Steel Sheet",
      "required_quantity": 4.0,
      "available_quantity": 4.0,
      "status": "available"
    },
    {
      "raw_material": "Pipe",
      "required_quantity": 2.0,
      "available_quantity": 30.0,
      "status": "available"
    }
  ]
}
```

---

## Step 16: Issue Material

**`POST http://localhost:8000/api/production/job-orders/12/issue-material/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{
  "issued_to": 23
}
```

**Response - HTTP 201**

```json
{
  "id": 6,
  "slip_no": "MIS-0006",
  "job_order": 12,
  "job_no": "JO-0012",
  "issue_date": "2026-08-06",
  "issued_to": 23,
  "issued_to_name": "apitester@crm.local",
  "status": "issued",
  "created_by": 23,
  "created_by_name": "apitester@crm.local",
  "items": [
    {
      "id": 11,
      "raw_material": 27,
      "raw_material_name": "Steel Sheet",
      "quantity": "4.00",
      "warehouse": 18,
      "warehouse_name": "Main Store"
    },
    {
      "id": 12,
      "raw_material": 28,
      "raw_material_name": "Pipe",
      "quantity": "2.00",
      "warehouse": 18,
      "warehouse_name": "Main Store"
    }
  ],
  "created_at": "2026-08-06T12:47:18.666208+05:30",
  "updated_at": "2026-08-06T12:47:18.666208+05:30"
}
```

---

## Step 17: Start Processes

**`POST http://localhost:8000/api/production/job-orders/12/start/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{
  "machine": 1,
  "supervisor": 23,
  "operators": [
    23
  ]
}
```

**Response - HTTP 200**

```json
{
  "id": 12,
  "job_no": "JO-0012",
  "sales_order": 40,
  "sales_order_id_ref": "SO-0040",
  "quotation": 14,
  "customer": 18,
  "customer_name": "Acme Corp Test",
  "product": 29,
  "product_name": "Steel Cabinet",
  "quantity": 1,
  "start_date": "2026-08-06",
  "end_date": null,
  "priority": "medium",
  "status": "in_production",
  "status_display": "In Production",
  "progress": 10,
  "machine": 1,
  "machine_name": "CNC Cutting Machine",
  "supervisor": 23,
  "supervisor_name": "apitester@crm.local",
  "operators": [
    23
  ],
  "bom": 1,
  "bom_name": "Cabinet BOM",
  "notes": "",
  "material_requirements": [
    {
      "id": 23,
      "raw_material": 27,
      "raw_material_name": "Steel Sheet",
      "required_quantity": "4.00",
      "available_quantity": "4.00",
      "issued_quantity": "4.00",
      "status": "issued",
      "updated_at": "2026-08-06T12:47:18.619223+05:30"
    },
    {
      "id": 24,
      "raw_material": 28,
      "raw_material_name": "Pipe",
      "required_quantity": "2.00",
      "available_quantity": "30.00",
      "issued_quantity": "2.00",
      "status": "issued",
      "updated_at": "2026-08-06T12:47:18.627210+05:30"
    }
  ],
  "processes": [
    {
      "id": 65,
      "sequence": 1,
      "name": "cutting",
      "status": "in_progress",
      "started_at": "2026-08-06T12:47:18.746208+05:30",
      "completed_at": null,
      "notes": ""
    },
    {
      "id": 66,
      "sequence": 2,
      "name": "fabrication",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "notes": ""
    },
    {
      "id": 67,
      "sequence": 3,
      "name": "machining",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "notes": ""
    },
    {
      "id": 68,
      "sequence": 4,
      "name": "welding",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "notes": ""
    },
    {
      "id": 69,
      "sequence": 5,
      "name": "grinding",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "notes": ""
    },
    {
      "id": 70,
      "sequence": 6,
      "name": "painting",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "notes": ""
    },
    {
      "id": 71,
      "sequence": 7,
      "name": "assembly",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "notes": ""
    },
    {
      "id": 72,
      "sequence": 8,
      "name": "qc",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "notes": ""
    }
  ],
  "finished_goods": [],
  "created_at": "2026-08-06T12:47:18.268208+05:30",
  "updated_at": "2026-08-06T12:47:18.755215+05:30"
}
```

---

## Step 18: Get Job Order Detail

**`GET http://localhost:8000/api/production/job-orders/12/`**

**Headers**

```
Authorization: Bearer <access_token>
```

**Response - HTTP 200**

```json
{
  "id": 12,
  "job_no": "JO-0012",
  "sales_order": 40,
  "sales_order_id_ref": "SO-0040",
  "quotation": 14,
  "customer": 18,
  "customer_name": "Acme Corp Test",
  "product": 29,
  "product_name": "Steel Cabinet",
  "quantity": 1,
  "start_date": "2026-08-06",
  "end_date": null,
  "priority": "medium",
  "status": "in_production",
  "status_display": "In Production",
  "progress": 10,
  "machine": 1,
  "machine_name": "CNC Cutting Machine",
  "supervisor": 23,
  "supervisor_name": "apitester@crm.local",
  "operators": [
    23
  ],
  "bom": 1,
  "bom_name": "Cabinet BOM",
  "notes": "",
  "material_requirements": [
    {
      "id": 23,
      "raw_material": 27,
      "raw_material_name": "Steel Sheet",
      "required_quantity": "4.00",
      "available_quantity": "4.00",
      "issued_quantity": "4.00",
      "status": "issued",
      "updated_at": "2026-08-06T12:47:18.619223+05:30"
    },
    {
      "id": 24,
      "raw_material": 28,
      "raw_material_name": "Pipe",
      "required_quantity": "2.00",
      "available_quantity": "30.00",
      "issued_quantity": "2.00",
      "status": "issued",
      "updated_at": "2026-08-06T12:47:18.627210+05:30"
    }
  ],
  "processes": [
    {
      "id": 65,
      "sequence": 1,
      "name": "cutting",
      "status": "in_progress",
      "started_at": "2026-08-06T12:47:18.746208+05:30",
      "completed_at": null,
      "notes": ""
    },
    {
      "id": 66,
      "sequence": 2,
      "name": "fabrication",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "notes": ""
    },
    {
      "id": 67,
      "sequence": 3,
      "name": "machining",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "notes": ""
    },
    {
      "id": 68,
      "sequence": 4,
      "name": "welding",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "notes": ""
    },
    {
      "id": 69,
      "sequence": 5,
      "name": "grinding",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "notes": ""
    },
    {
      "id": 70,
      "sequence": 6,
      "name": "painting",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "notes": ""
    },
    {
      "id": 71,
      "sequence": 7,
      "name": "assembly",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "notes": ""
    },
    {
      "id": 72,
      "sequence": 8,
      "name": "qc",
      "status": "pending",
      "started_at": null,
      "completed_at": null,
      "notes": ""
    }
  ],
  "finished_goods": [],
  "created_at": "2026-08-06T12:47:18.268208+05:30",
  "updated_at": "2026-08-06T12:47:18.755215+05:30"
}
```

---

## Step 19.1: Advance Process 1/8

**`POST http://localhost:8000/api/production/processes/65/advance/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 200**

```json
{
  "id": 65,
  "sequence": 1,
  "name": "cutting",
  "status": "completed",
  "started_at": "2026-08-06T12:47:18.746208+05:30",
  "completed_at": "2026-08-06T12:47:18.818207+05:30",
  "notes": ""
}
```

---

## Step 19.2: Advance Process 2/8

**`POST http://localhost:8000/api/production/processes/66/advance/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 200**

```json
{
  "id": 66,
  "sequence": 2,
  "name": "fabrication",
  "status": "completed",
  "started_at": "2026-08-06T12:47:18.825209+05:30",
  "completed_at": "2026-08-06T12:47:18.837207+05:30",
  "notes": ""
}
```

---

## Step 19.3: Advance Process 3/8

**`POST http://localhost:8000/api/production/processes/67/advance/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 200**

```json
{
  "id": 67,
  "sequence": 3,
  "name": "machining",
  "status": "completed",
  "started_at": "2026-08-06T12:47:18.845209+05:30",
  "completed_at": "2026-08-06T12:47:18.854208+05:30",
  "notes": ""
}
```

---

## Step 19.4: Advance Process 4/8

**`POST http://localhost:8000/api/production/processes/68/advance/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 200**

```json
{
  "id": 68,
  "sequence": 4,
  "name": "welding",
  "status": "completed",
  "started_at": "2026-08-06T12:47:18.860213+05:30",
  "completed_at": "2026-08-06T12:47:18.869209+05:30",
  "notes": ""
}
```

---

## Step 19.5: Advance Process 5/8

**`POST http://localhost:8000/api/production/processes/69/advance/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 200**

```json
{
  "id": 69,
  "sequence": 5,
  "name": "grinding",
  "status": "completed",
  "started_at": "2026-08-06T12:47:18.875208+05:30",
  "completed_at": "2026-08-06T12:47:18.884207+05:30",
  "notes": ""
}
```

---

## Step 19.6: Advance Process 6/8

**`POST http://localhost:8000/api/production/processes/70/advance/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 200**

```json
{
  "id": 70,
  "sequence": 6,
  "name": "painting",
  "status": "completed",
  "started_at": "2026-08-06T12:47:18.890207+05:30",
  "completed_at": "2026-08-06T12:47:18.903208+05:30",
  "notes": ""
}
```

---

## Step 19.7: Advance Process 7/8

**`POST http://localhost:8000/api/production/processes/71/advance/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 200**

```json
{
  "id": 71,
  "sequence": 7,
  "name": "assembly",
  "status": "completed",
  "started_at": "2026-08-06T12:47:18.910209+05:30",
  "completed_at": "2026-08-06T12:47:18.918214+05:30",
  "notes": ""
}
```

---

## Step 19.8: Advance Process 8/8

**`POST http://localhost:8000/api/production/processes/72/advance/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 200**

```json
{
  "id": 72,
  "sequence": 8,
  "name": "qc",
  "status": "completed",
  "started_at": "2026-08-06T12:47:18.925214+05:30",
  "completed_at": "2026-08-06T12:47:18.934209+05:30",
  "notes": ""
}
```

---

## Step 20: Job Order QC

**`POST http://localhost:8000/api/production/job-orders/12/qc/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{
  "passed": true,
  "warehouse": 18,
  "notes": "All checks passed"
}
```

**Response - HTTP 200**

```json
{
  "job_order": {
    "id": 12,
    "job_no": "JO-0012",
    "sales_order": 40,
    "sales_order_id_ref": "SO-0040",
    "quotation": 14,
    "customer": 18,
    "customer_name": "Acme Corp Test",
    "product": 29,
    "product_name": "Steel Cabinet",
    "quantity": 1,
    "start_date": "2026-08-06",
    "end_date": null,
    "priority": "medium",
    "status": "qc_passed",
    "status_display": "QC Passed",
    "progress": 95,
    "machine": 1,
    "machine_name": "CNC Cutting Machine",
    "supervisor": 23,
    "supervisor_name": "apitester@crm.local",
    "operators": [
      23
    ],
    "bom": 1,
    "bom_name": "Cabinet BOM",
    "notes": "",
    "material_requirements": [
      {
        "id": 23,
        "raw_material": 27,
        "raw_material_name": "Steel Sheet",
        "required_quantity": "4.00",
        "available_quantity": "4.00",
        "issued_quantity": "4.00",
        "status": "issued",
        "updated_at": "2026-08-06T12:47:18.619223+05:30"
      },
      {
        "id": 24,
        "raw_material": 28,
        "raw_material_name": "Pipe",
        "required_quantity": "2.00",
        "available_quantity": "30.00",
        "issued_quantity": "2.00",
        "status": "issued",
        "updated_at": "2026-08-06T12:47:18.627210+05:30"
      }
    ],
    "processes": [
      {
        "id": 65,
        "sequence": 1,
        "name": "cutting",
        "status": "completed",
        "started_at": "2026-08-06T12:47:18.746208+05:30",
        "completed_at": "2026-08-06T12:47:18.818207+05:30",
        "notes": ""
      },
      {
        "id": 66,
        "sequence": 2,
        "name": "fabrication",
        "status": "completed",
        "started_at": "2026-08-06T12:47:18.825209+05:30",
        "completed_at": "2026-08-06T12:47:18.837207+05:30",
        "notes": ""
      },
      {
        "id": 67,
        "sequence": 3,
        "name": "machining",
        "status": "completed",
        "started_at": "2026-08-06T12:47:18.845209+05:30",
        "completed_at": "2026-08-06T12:47:18.854208+05:30",
        "notes": ""
      },
      {
        "id": 68,
        "sequence": 4,
        "name": "welding",
        "status": "completed",
        "started_at": "2026-08-06T12:47:18.860213+05:30",
        "completed_at": "2026-08-06T12:47:18.869209+05:30",
        "notes": ""
      },
      {
        "id": 69,
        "sequence": 5,
        "name": "grinding",
        "status": "completed",
        "started_at": "2026-08-06T12:47:18.875208+05:30",
        "completed_at": "2026-08-06T12:47:18.884207+05:30",
        "notes": ""
      },
      {
        "id": 70,
        "sequence": 6,
        "name": "painting",
        "status": "completed",
        "started_at": "2026-08-06T12:47:18.890207+05:30",
        "completed_at": "2026-08-06T12:47:18.903208+05:30",
        "notes": ""
      },
      {
        "id": 71,
        "sequence": 7,
        "name": "assembly",
        "status": "completed",
        "started_at": "2026-08-06T12:47:18.910209+05:30",
        "completed_at": "2026-08-06T12:47:18.918214+05:30",
        "notes": ""
      },
      {
        "id": 72,
        "sequence": 8,
        "name": "qc",
        "status": "completed",
        "started_at": "2026-08-06T12:47:18.925214+05:30",
        "completed_at": "2026-08-06T12:47:18.963211+05:30",
        "notes": ""
      }
    ],
    "finished_goods": [
      {
        "id": 4,
        "finished_goods_no": "FG-0004",
        "job_order": 12,
        "job_no": "JO-0012",
        "product": 29,
        "product_name": "Steel Cabinet",
        "quantity": 1,
        "batch_no": "BJO-0012-20260806",
        "barcode": "FG000004",
        "warehouse": 18,
        "status": "in_stock",
        "created_at": "2026-08-06T12:47:18.960208+05:30",
        "updated_at": "2026-08-06T12:47:18.960208+05:30"
      }
    ],
    "created_at": "2026-08-06T12:47:18.268208+05:30",
    "updated_at": "2026-08-06T12:47:18.964210+05:30"
  },
  "finished_goods": {
    "id": 4,
    "finished_goods_no": "FG-0004",
    "job_order": 12,
    "job_no": "JO-0012",
    "product": 29,
    "product_name": "Steel Cabinet",
    "quantity": 1,
    "batch_no": "BJO-0012-20260806",
    "barcode": "FG000004",
    "warehouse": 18,
    "status": "in_stock",
    "created_at": "2026-08-06T12:47:18.960208+05:30",
    "updated_at": "2026-08-06T12:47:18.960208+05:30"
  }
}
```

---

## Step 21: Dispatch Job

**`POST http://localhost:8000/api/production/job-orders/12/dispatch/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{
  "packing_note": "Box 1 of 1",
  "transport_mode": "road",
  "vehicle_number": "KA01 AB 1234",
  "driver_name": "Ravi Kumar",
  "driver_phone": "9876543210",
  "label_printed": true
}
```

**Response - HTTP 201**

```json
{
  "id": 4,
  "dispatch_no": "DS-0004",
  "job_order": 12,
  "job_no": "JO-0012",
  "sales_order": 40,
  "sales_order_id_ref": "SO-0040",
  "customer": 18,
  "customer_name": "Acme Corp Test",
  "delivery_note": 12,
  "delivery_note_id_ref": "DN-0012",
  "packing_note": "Box 1 of 1",
  "label_printed": true,
  "transport_mode": "road",
  "vehicle_number": "KA01 AB 1234",
  "driver_name": "Ravi Kumar",
  "driver_phone": "9876543210",
  "status": "ready",
  "status_display": "Ready",
  "dispatch_date": null,
  "created_at": "2026-08-06T12:47:19.014208+05:30",
  "updated_at": "2026-08-06T12:47:19.051213+05:30"
}
```

---

## Step 22: Mark Dispatch Dispatched

**`POST http://localhost:8000/api/production/dispatches/4/mark-dispatched/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{
  "vehicle_number": "KA01 AB 1234",
  "driver_name": "Ravi Kumar",
  "driver_phone": "9876543210"
}
```

**Response - HTTP 200**

```json
{
  "id": 4,
  "dispatch_no": "DS-0004",
  "job_order": 12,
  "job_no": "JO-0012",
  "sales_order": 40,
  "sales_order_id_ref": "SO-0040",
  "customer": 18,
  "customer_name": "Acme Corp Test",
  "delivery_note": 12,
  "delivery_note_id_ref": "DN-0012",
  "packing_note": "Box 1 of 1",
  "label_printed": true,
  "transport_mode": "road",
  "vehicle_number": "KA01 AB 1234",
  "driver_name": "Ravi Kumar",
  "driver_phone": "9876543210",
  "status": "dispatched",
  "status_display": "Dispatched",
  "dispatch_date": "2026-08-06",
  "created_at": "2026-08-06T12:47:19.014208+05:30",
  "updated_at": "2026-08-06T12:47:19.068206+05:30"
}
```

---

## Step 23: Create Invoice From Delivery Note

**`POST http://localhost:8000/api/sales/delivery-notes/12/create-invoice/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{
  "due_in_days": 15
}
```

**Response - HTTP 201**

```json
{
  "id": 7,
  "invoice_number": "INV-0007",
  "sales_order": null,
  "sales_order_id_ref": "",
  "delivery_note": 12,
  "delivery_note_id_ref": "DN-0012",
  "customer_name": "Acme Corp Test",
  "customer_email": "acme.test@example.com",
  "customer_address": "",
  "billing_address": "",
  "invoice_date": "2026-08-06",
  "due_date": "2026-08-21",
  "payment_method": "cash",
  "transaction_id": "",
  "subtotal": "800.00",
  "tax": null,
  "tax_percentage": "0.00",
  "tax_amount": "0.00",
  "discount_percentage": "0.00",
  "discount_amount": "0.00",
  "total": "800.00",
  "status": "sent",
  "notes": "",
  "terms_conditions": "",
  "created_by": 23,
  "created_at": "2026-08-06T12:47:19.106207+05:30",
  "updated_at": "2026-08-06T12:47:19.106207+05:30",
  "items": [
    {
      "id": 9,
      "invoice": 7,
      "description": "Steel Cabinet",
      "quantity": 1,
      "unit_price": "800.00",
      "total": "800.00"
    }
  ]
}
```

---

## Step 24: Mark Invoice Paid

**`POST http://localhost:8000/api/invoices/invoices/7/mark-paid/`**

**Headers**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request body**

```json
{}
```

**Response - HTTP 200**

```json
{
  "id": 7,
  "invoice_number": "INV-0007",
  "sales_order": null,
  "sales_order_id_ref": "",
  "delivery_note": 12,
  "delivery_note_id_ref": "DN-0012",
  "customer_name": "Acme Corp Test",
  "customer_email": "acme.test@example.com",
  "customer_address": "",
  "billing_address": "",
  "invoice_date": "2026-08-06",
  "due_date": "2026-08-21",
  "payment_method": "cash",
  "transaction_id": "",
  "subtotal": "800.00",
  "tax": null,
  "tax_percentage": "0.00",
  "tax_amount": "0.00",
  "discount_percentage": "0.00",
  "discount_amount": "0.00",
  "total": "800.00",
  "status": "paid",
  "notes": "",
  "terms_conditions": "",
  "created_by": 23,
  "created_at": "2026-08-06T12:47:19.106207+05:30",
  "updated_at": "2026-08-06T12:47:19.136207+05:30",
  "items": [
    {
      "id": 9,
      "invoice": 7,
      "description": "Steel Cabinet",
      "quantity": 1,
      "unit_price": "800.00",
      "total": "800.00"
    }
  ]
}
```

---

## Step 25: Verify Invoice Paid

**`GET http://localhost:8000/api/invoices/invoices/7/`**

**Headers**

```
Authorization: Bearer <access_token>
```

**Response - HTTP 200**

```json
{
  "id": 7,
  "invoice_number": "INV-0007",
  "sales_order": null,
  "sales_order_id_ref": "",
  "delivery_note": 12,
  "delivery_note_id_ref": "DN-0012",
  "customer_name": "Acme Corp Test",
  "customer_email": "acme.test@example.com",
  "customer_address": "",
  "billing_address": "",
  "invoice_date": "2026-08-06",
  "due_date": "2026-08-21",
  "payment_method": "cash",
  "transaction_id": "",
  "subtotal": "800.00",
  "tax": null,
  "tax_percentage": "0.00",
  "tax_amount": "0.00",
  "discount_percentage": "0.00",
  "discount_amount": "0.00",
  "total": "800.00",
  "status": "paid",
  "notes": "",
  "terms_conditions": "",
  "created_by": 23,
  "created_at": "2026-08-06T12:47:19.106207+05:30",
  "updated_at": "2026-08-06T12:47:19.136207+05:30",
  "items": [
    {
      "id": 9,
      "invoice": 7,
      "description": "Steel Cabinet",
      "quantity": 1,
      "unit_price": "800.00",
      "total": "800.00"
    }
  ]
}
```

> **Note:** payments on this invoice: 1

---

## End state (verified)

- Lead status = `won`
- Quotation status = `accepted`
- Sales Order status = `completed`
- Job Order status = `completed` (progress 100%)
- GRN status = `accepted`; QualityInspection = `passed`
- FinishedGoods = `dispatched`
- Dispatch status = `dispatched`; DeliveryNote created automatically
- Invoice status = `paid` with 1 Payment record
- Main Store stock after the run: **Steel Sheet = 0, Pipe = 28**

---

> Tip: these exact requests are also available in `CRM_System_Postman_Collection.json`
> under **36. PRODUCTION** and the updated **8. SALES / 12. ORDERS / 17. INVOICES** folders.