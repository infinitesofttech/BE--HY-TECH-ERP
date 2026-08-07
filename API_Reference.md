# CRM System - Complete API Reference

All **389** REST endpoints exposed by the backend, grouped by app module.

**Base URL:** `http://localhost:8000`  
**Auth:** Bearer token - call `POST /api/auth/login/`, then send `Authorization: Bearer <access_token>` on every request.
Interactive docs are available at **`/api/docs/`** (Swagger UI) and the raw OpenAPI schema at **`/api/schema/`**.

| # | App | Endpoints |
|---|-----|-----------|
| 1 | OpenAPI Schema | 1 |
| 2 | Swagger UI | 1 |
| 3 | Accounts & Authentication | 22 |
| 4 | assets | 11 |
| 5 | Attendance | 9 |
| 6 | GPS / Location Tracking | 5 |
| 7 | Masters - Dealers | 3 |
| 8 | Masters - Retailers | 3 |
| 9 | Visits | 7 |
| 10 | Products & Inventory | 25 |
| 11 | Sales Orders | 20 |
| 12 | Purchases (Purchase Orders) | 9 |
| 13 | Production & Manufacturing | 33 |
| 14 | Targets | 8 |
| 15 | Leaves | 15 |
| 16 | Notifications | 7 |
| 17 | Orders (Quotations & Work Orders) | 11 |
| 18 | Reports | 14 |
| 19 | Pipeline (Leads) | 15 |
| 20 | Contacts | 7 |
| 21 | Invoices | 5 |
| 22 | Projects | 13 |
| 23 | Contracts | 2 |
| 24 | Email Marketing | 7 |
| 25 | Chat | 5 |
| 26 | Tickets / Support | 4 |
| 27 | Blog | 8 |
| 28 | Masters - Configuration | 14 |
| 29 | Subscriptions | 9 |
| 30 | Marketing | 4 |
| 31 | Finance | 27 |
| 32 | Estimations | 4 |
| 33 | Settings Configuration | 27 |
| 34 | Content Management | 13 |
| 35 | System Admin | 12 |
| 36 | Calendar Events | 5 |
| 37 | Invitations | 4 |

---

## OpenAPI Schema

`1` endpoints under **`/api/schema/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET | `/api/schema/` | OpenApi3 schema for this API. Format can be selected via content negotiation. | `SpectacularAPIView`<br>(no serializer_class) |

## Swagger UI

`1` endpoints under **`/api/docs/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET | `/api/docs/` | Swagger ui | `SpectacularSwaggerView`<br>(no serializer_class) |

## Accounts & Authentication

`22` endpoints under **`/api/auth/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/auth/activity-logs/` | Activity log list | `UserActivityLogListCreateView`<br>model `UserActivityLog`<br>ser `UserActivityLogSerializer`<br><small>fields: `id, user, user_name, action, module, record_id, ip_address, action_date`</small> |
| POST | `/api/auth/change-password/` | Change password | `ChangePasswordView`<br>(no serializer_class) |
| GET, POST, PUT | `/api/auth/contact/` | Contact info | `ContactInfoView`<br>(no serializer_class) |
| POST | `/api/auth/delete-request/` | Delete request | `DeleteAccountRequestView`<br>(no serializer_class) |
| GET | `/api/auth/devices/` | Device list | `DeviceListView`<br>(no serializer_class) |
| GET | `/api/auth/employees/` | Employee list | `EmployeeListView`<br>ser `UserSerializer` |
| POST | `/api/auth/feedback/` | Feedback create | `FeedbackCreateView`<br>model `Feedback`<br>ser `FeedbackSerializer`<br><small>fields: `id, name, email, phone, message, created_at`</small> |
| POST | `/api/auth/forgot-password/` | Forgot password | `ForgotPasswordView`<br>(no serializer_class) |
| GET | `/api/auth/login-logs/` | Login log list | `LoginLogListView`<br>model `LoginLog`<br>ser `LoginLogSerializer` |
| POST | `/api/auth/login/` | Login | `LoginView`<br>(no serializer_class) |
| POST | `/api/auth/logout/` | Logout | `LogoutView`<br>(no serializer_class) |
| GET, PUT | `/api/auth/profile/` | Profile | `ProfileView`<br>(no serializer_class) |
| POST | `/api/auth/register-device/` | Register device | `RegisterDeviceTokenView`<br>(no serializer_class) |
| POST | `/api/auth/register/` | Register | `RegisterView`<br>(no serializer_class) |
| GET, POST | `/api/auth/roles/` | Role list | `RoleListCreateView`<br>model `Role`<br>ser `RoleSerializer`<br><small>fields: `id, name, permissions, created_at`</small> |
| GET | `/api/auth/company/dashboard/` | Company dashboard | `CompanyDashboardView`<br>(no serializer_class) |
| GET, PATCH | `/api/auth/company/profile/` | Company profile | `CompanyProfileView`<br>(no serializer_class) |
| POST | `/api/auth/company/register/` | Company register | `CompanyRegisterView`<br>(no serializer_class) |
| GET, PUT, PATCH | `/api/auth/employees/{id}/` | Employee detail | `EmployeeDetailView`<br>model `User`<br>ser `UserSerializer`<br><small>fields: `id, email, first_name, last_name, username, role, phone, avatar, territory, pin_code, manager, manager_name, device_token, address, city, state, date_of_birth, joining_date, department, department_name, designation, designation_name, shift_...`</small> |
| GET | `/api/auth/feedback/list/` | Feedback list | `FeedbackListView`<br>model `Feedback`<br>ser `FeedbackSerializer` |
| GET, PUT, PATCH, DELETE | `/api/auth/roles/{id}/` | Role detail | `RoleDetailView`<br>model `Role`<br>ser `RoleSerializer`<br><small>fields: `id, name, permissions, created_at`</small> |
| PATCH | `/api/auth/employees/{id}/toggle-active/` | Employee toggle active | `EmployeeToggleActiveView`<br>(no serializer_class) |

## assets

`11` endpoints under **`/api/assets/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET | `/api/assets/analytics/` | Asset analytics | `AssetAnalyticsView`<br>(no serializer_class) |
| GET, POST | `/api/assets/assignments/` | Asset assignment list | `AssetAssignmentListCreateView`<br>model `AssetAssignment`<br>ser `AssetAssignmentSerializer`<br><small>fields: `id, assignment_id, asset, asset_name, assigned_to, assigned_to_name, department, assignment_date, return_date, status, created_at, updated_at`</small> |
| GET, POST | `/api/assets/depreciations/` | Asset depreciation list | `AssetDepreciationListCreateView`<br>model `AssetDepreciation`<br>ser `AssetDepreciationSerializer`<br><small>fields: `id, depreciation_id, asset, asset_name, purchase_cost, accumulated_depreciation, net_book_value, depreciation_method, useful_life_years, status, created_at, updated_at`</small> |
| GET, POST | `/api/assets/disposals/` | Asset disposal list | `AssetDisposalListCreateView`<br>model `AssetDisposal`<br>ser `AssetDisposalSerializer`<br><small>fields: `id, disposal_id, asset, asset_name, method, value, date, approved_by, approved_by_name, status, created_at, updated_at`</small> |
| GET, POST | `/api/assets/maintenances/` | Asset maintenance list | `AssetMaintenanceListCreateView`<br>model `AssetMaintenance`<br>ser `AssetMaintenanceSerializer`<br><small>fields: `id, maintenance_id, asset, asset_name, maintenance_type, scheduled_date, remark, status, created_at, updated_at`</small> |
| GET, POST | `/api/assets/registrations/` | Asset registration list | `AssetRegistrationListCreateView`<br>model `AssetRegistration`<br>ser `AssetRegistrationSerializer`<br><small>fields: `id, asset_name, asset_user, asset_user_name, category, location, purchase_date, warranty_end_date, warranty, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/assets/assignments/{id}/` | Asset assignment detail | `AssetAssignmentDetailView`<br>model `AssetAssignment`<br>ser `AssetAssignmentSerializer`<br><small>fields: `id, assignment_id, asset, asset_name, assigned_to, assigned_to_name, department, assignment_date, return_date, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/assets/depreciations/{id}/` | Asset depreciation detail | `AssetDepreciationDetailView`<br>model `AssetDepreciation`<br>ser `AssetDepreciationSerializer`<br><small>fields: `id, depreciation_id, asset, asset_name, purchase_cost, accumulated_depreciation, net_book_value, depreciation_method, useful_life_years, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/assets/disposals/{id}/` | Asset disposal detail | `AssetDisposalDetailView`<br>model `AssetDisposal`<br>ser `AssetDisposalSerializer`<br><small>fields: `id, disposal_id, asset, asset_name, method, value, date, approved_by, approved_by_name, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/assets/maintenances/{id}/` | Asset maintenance detail | `AssetMaintenanceDetailView`<br>model `AssetMaintenance`<br>ser `AssetMaintenanceSerializer`<br><small>fields: `id, maintenance_id, asset, asset_name, maintenance_type, scheduled_date, remark, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/assets/registrations/{id}/` | Asset registration detail | `AssetRegistrationDetailView`<br>model `AssetRegistration`<br>ser `AssetRegistrationSerializer`<br><small>fields: `id, asset_name, asset_user, asset_user_name, category, location, purchase_date, warranty_end_date, warranty, status, created_at, updated_at`</small> |

## Attendance

`9` endpoints under **`/api/attendance/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET | `/api/attendance/history/` | Attendance history | `AttendanceHistoryView`<br>ser `AttendanceSerializer` |
| POST | `/api/attendance/punch-in/` | Attendance punch in | `AttendancePunchInView`<br>(no serializer_class) |
| POST | `/api/attendance/punch-out/` | Attendance punch out | `AttendancePunchOutView`<br>(no serializer_class) |
| GET | `/api/attendance/today/` | Attendance today | `TodayAttendanceView`<br>(no serializer_class) |
| GET, POST | `/api/attendance/types/` | Attendance types | `AttendanceTypeListCreateView`<br>model `AttendanceType`<br>ser `AttendanceTypeSerializer`<br><small>fields: `id, name, is_active, created_at`</small> |
| GET | `/api/attendance/report/daily/` | Attendance report daily | `AttendanceDailyReportView`<br>(no serializer_class) |
| GET | `/api/attendance/report/export/` | Attendance report export | `AttendanceExportView`<br>(no serializer_class) |
| GET | `/api/attendance/report/monthly/` | Attendance report monthly | `AttendanceMonthlyReportView`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/attendance/types/{id}/` | Attendance type detail | `AttendanceTypeDetailView`<br>model `AttendanceType`<br>ser `AttendanceTypeSerializer`<br><small>fields: `id, name, is_active, created_at`</small> |

## GPS / Location Tracking

`5` endpoints under **`/api/tracking/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET | `/api/tracking/history/` | Tracking history | `TrackingHistoryView`<br>ser `TrackingLocationSerializer` |
| GET | `/api/tracking/live/` | Live locations | `LiveLocationsView`<br>(no serializer_class) |
| POST | `/api/tracking/location/` | Location update | `LocationUpdateView`<br>(no serializer_class) |
| GET | `/api/tracking/distance/{employee_id}/` | Daily distance | `DailyDistanceView`<br>(no serializer_class) |
| GET | `/api/tracking/route/{employee_id}/` | Route history | `RouteHistoryView`<br>(no serializer_class) |

## Masters - Dealers

`3` endpoints under **`/api/dealers/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/dealers/` | Dealer list | `DealerListCreateView`<br>model `Dealer`<br>ser `DealerSerializer`<br><small>fields: `id, assigned_to_name, name, contact_person, phone, email, address, city, state, pin_code, latitude, longitude, status, created_at, updated_at, assigned_to, managed_by`</small> |
| GET, PUT, PATCH, DELETE | `/api/dealers/{id}/` | Dealer detail | `DealerDetailView`<br>model `Dealer`<br>ser `DealerSerializer`<br><small>fields: `id, assigned_to_name, name, contact_person, phone, email, address, city, state, pin_code, latitude, longitude, status, created_at, updated_at, assigned_to, managed_by`</small> |
| PATCH | `/api/dealers/{id}/toggle-status/` | Dealer toggle status | `DealerToggleStatusView`<br>(no serializer_class) |

## Masters - Retailers

`3` endpoints under **`/api/retailers/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/retailers/` | Retailer list | `RetailerListCreateView`<br>model `Retailer`<br>ser `RetailerSerializer`<br><small>fields: `id, assigned_to_name, name, contact_person, phone, email, address, city, state, pin_code, latitude, longitude, status, created_at, updated_at, assigned_to, managed_by`</small> |
| GET, PUT, PATCH, DELETE | `/api/retailers/{id}/` | Retailer detail | `RetailerDetailView`<br>model `Retailer`<br>ser `RetailerSerializer`<br><small>fields: `id, assigned_to_name, name, contact_person, phone, email, address, city, state, pin_code, latitude, longitude, status, created_at, updated_at, assigned_to, managed_by`</small> |
| PATCH | `/api/retailers/{id}/toggle-status/` | Retailer toggle status | `RetailerToggleStatusView`<br>(no serializer_class) |

## Visits

`7` endpoints under **`/api/visits/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET | `/api/visits/` | Visit list | `VisitListView`<br>ser `VisitSerializer` |
| GET | `/api/visits/{id}/` | Visit detail | `VisitDetailView`<br>ser `VisitSerializer` |
| POST | `/api/visits/check-in/` | Visit check in | `VisitCheckInView`<br>(no serializer_class) |
| POST | `/api/visits/check-out/` | Visit check out | `VisitCheckOutView`<br>(no serializer_class) |
| GET | `/api/visits/export/` | Visit export | `VisitExportView`<br>(no serializer_class) |
| GET | `/api/visits/report/` | Visit report | `VisitReportView`<br>(no serializer_class) |
| GET | `/api/visits/today/` | Visit today | `TodayVisitsView`<br>(no serializer_class) |

## Products & Inventory

`25` endpoints under **`/api/products/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/products/` | Product list | `ProductListCreateView`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/products/{id}/` | Product detail | `ProductDetailView`<br>model `Product`<br>(no serializer_class) |
| GET | `/api/products/catalogue/` | Product catalogue | `ProductCatalogueView`<br>(no serializer_class) |
| GET, POST | `/api/products/categories/` | Product category list | `ProductCategoryListCreateView`<br>model `ProductCategory`<br>ser `ProductCategorySerializer`<br><small>fields: `id, name, slug, status, product_count, created_at`</small> |
| GET, POST | `/api/products/inventories/` | Inventory list | `InventoryListCreateView`<br>model `Inventory`<br>ser `InventorySerializer`<br><small>fields: `id, product, product_name, warehouse, warehouse_name, quantity, status, created_at, updated_at`</small> |
| GET, POST | `/api/products/policies/` | Policy list | `PolicyListCreateView`<br>model `Policy`<br>ser `PolicySerializer`<br><small>fields: `id, title, description, category, attachment, is_active, created_at, updated_at`</small> |
| GET, POST | `/api/products/stock-adjustments/` | Stock adjustment list | `StockAdjustmentListCreateView`<br>model `StockAdjustment`<br>ser `StockAdjustmentSerializer`<br><small>fields: `id, product, product_name, warehouse, warehouse_name, reason, difference, adjustment_date, created_at`</small> |
| GET, POST | `/api/products/stock-transfers/` | Stock transfer list | `StockTransferListCreateView`<br>model `StockTransfer`<br>ser `StockTransferSerializer`<br><small>fields: `id, product, product_name, from_warehouse, from_warehouse_name, to_warehouse, to_warehouse_name, quantity, transfer_date, status, created_at, updated_at`</small> |
| GET, POST | `/api/products/suppliers/` | Supplier list | `SupplierListCreateView`<br>model `Supplier`<br>ser `SupplierSerializer`<br><small>fields: `id, name, email, phone, country, status, created_at, updated_at`</small> |
| GET, POST | `/api/products/tour-plans/` | Tour plan list | `TourPlanListCreateView`<br>model `TourPlan`<br>ser `TourPlanSerializer`<br><small>fields: `id, name, description, tour_type, start_date, end_date, duration_days, plan_details, is_active, created_at`</small> |
| GET, POST | `/api/products/warehouses/` | Warehouse list | `WarehouseListCreateView`<br>model `Warehouse`<br>ser `WarehouseSerializer`<br><small>fields: `id, name, contact_person, phone, capacity, status, created_at, updated_at`</small> |
| PATCH | `/api/products/{id}/toggle-active/` | Product toggle active | `ProductToggleActiveView`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/products/categories/{id}/` | Product category detail | `ProductCategoryDetailView`<br>model `ProductCategory`<br>ser `ProductCategorySerializer`<br><small>fields: `id, name, slug, status, product_count, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/products/inventories/{id}/` | Inventory detail | `InventoryDetailView`<br>model `Inventory`<br>ser `InventorySerializer`<br><small>fields: `id, product, product_name, warehouse, warehouse_name, quantity, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/products/policies/{id}/` | Policy detail | `PolicyDetailView`<br>model `Policy`<br>ser `PolicySerializer`<br><small>fields: `id, title, description, category, attachment, is_active, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/products/stock-adjustments/{id}/` | Stock adjustment detail | `StockAdjustmentDetailView`<br>model `StockAdjustment`<br>ser `StockAdjustmentSerializer`<br><small>fields: `id, product, product_name, warehouse, warehouse_name, reason, difference, adjustment_date, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/products/stock-transfers/{id}/` | Stock transfer detail | `StockTransferDetailView`<br>model `StockTransfer`<br>ser `StockTransferSerializer`<br><small>fields: `id, product, product_name, from_warehouse, from_warehouse_name, to_warehouse, to_warehouse_name, quantity, transfer_date, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/products/suppliers/{id}/` | Supplier detail | `SupplierDetailView`<br>model `Supplier`<br>ser `SupplierSerializer`<br><small>fields: `id, name, email, phone, country, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/products/tour-plans/{id}/` | Tour plan detail | `TourPlanDetailView`<br>model `TourPlan`<br>ser `TourPlanSerializer`<br><small>fields: `id, name, description, tour_type, start_date, end_date, duration_days, plan_details, is_active, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/products/warehouses/{id}/` | Warehouse detail | `WarehouseDetailView`<br>model `Warehouse`<br>ser `WarehouseSerializer`<br><small>fields: `id, name, contact_person, phone, capacity, status, created_at, updated_at`</small> |
| PATCH | `/api/products/inventories/{id}/toggle-active/` | Inventory toggle | `InventoryToggleActiveView`<br>(no serializer_class) |
| PATCH | `/api/products/policies/{id}/toggle-active/` | Policy toggle | `PolicyToggleActiveView`<br>(no serializer_class) |
| PATCH | `/api/products/suppliers/{id}/toggle-active/` | Supplier toggle | `SupplierToggleActiveView`<br>(no serializer_class) |
| PATCH | `/api/products/tour-plans/{id}/toggle-active/` | Tour plan toggle | `TourPlanToggleActiveView`<br>(no serializer_class) |
| PATCH | `/api/products/warehouses/{id}/toggle-active/` | Warehouse toggle | `WarehouseToggleActiveView`<br>(no serializer_class) |

## Sales Orders

`20` endpoints under **`/api/sales/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET | `/api/sales/analysis/` | Sales analysis | `SalesAnalysisView`<br>(no serializer_class) |
| GET, POST | `/api/sales/customers/` | Customer list | `CustomerListCreateView`<br>model `Customer`<br>ser `CustomerSerializer`<br><small>fields: `id, name, email, phone, country, created_at, updated_at`</small> |
| GET | `/api/sales/daily/` | Sales daily | `DailySalesReportView`<br>(no serializer_class) |
| GET, POST | `/api/sales/delivery-notes/` | Delivery note list | `DeliveryNoteListCreateView`<br>model `DeliveryNote`<br>(no serializer_class) |
| GET | `/api/sales/export/` | Sales export | `SalesExportView`<br>(no serializer_class) |
| GET, POST | `/api/sales/feedback/` | Customer feedback list | `CustomerFeedbackListCreateView`<br>model `CustomerFeedback`<br>ser `CustomerFeedbackSerializer`<br><small>fields: `id, customer, customer_name, subject, feedback, date, status, created_at, updated_at`</small> |
| GET | `/api/sales/monthly/` | Sales monthly | `MonthlySalesReportView`<br>(no serializer_class) |
| GET, POST | `/api/sales/orders/` | Sales order list | `SalesOrderListCreateView`<br>model `SalesOrder`<br>(no serializer_class) |
| GET, POST | `/api/sales/refunds/` | Refund list | `RefundListCreateView`<br>model `Refund`<br>ser `RefundSerializer`<br><small>fields: `id, refund_id, reference, amount, customer, customer_name, payment_method, status, refund_reason, created_at, updated_at`</small> |
| GET | `/api/sales/reports/` | Sales report list | `SalesReportListView`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/sales/customers/{id}/` | Customer detail | `CustomerDetailView`<br>model `Customer`<br>ser `CustomerSerializer`<br><small>fields: `id, name, email, phone, country, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/sales/delivery-notes/{id}/` | Delivery note detail | `DeliveryNoteDetailView`<br>model `DeliveryNote`<br>(no serializer_class) |
| GET | `/api/sales/employee/{employee_id}/` | Sales employee | `EmployeeSalesView`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/sales/feedback/{id}/` | Customer feedback detail | `CustomerFeedbackDetailView`<br>model `CustomerFeedback`<br>ser `CustomerFeedbackSerializer`<br><small>fields: `id, customer, customer_name, subject, feedback, date, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/sales/orders/{id}/` | Sales order detail | `SalesOrderDetailView`<br>model `SalesOrder`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/sales/refunds/{id}/` | Refund detail | `RefundDetailView`<br>model `Refund`<br>ser `RefundSerializer`<br><small>fields: `id, refund_id, reference, amount, customer, customer_name, payment_method, status, refund_reason, created_at, updated_at`</small> |
| GET | `/api/sales/reports/{id}/` | Sales report detail | `SalesReportDetailView`<br>model `SalesOrder`<br>ser `SalesOrderSerializer` |
| POST | `/api/sales/delivery-notes/{id}/create-invoice/` | Delivery note create invoice | `DeliveryNoteCreateInvoiceView`<br>(no serializer_class) |
| PATCH | `/api/sales/delivery-notes/{id}/toggle-active/` | Delivery note toggle | `DeliveryNoteToggleActiveView`<br>(no serializer_class) |
| POST | `/api/sales/orders/{id}/start-production/` | Sales order start production | `SalesOrderStartProductionView`<br>(no serializer_class) |

## Purchases (Purchase Orders)

`9` endpoints under **`/api/purchases/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/purchases/` | Purchase list create | `PurchaseListCreateView`<br>model `Purchase`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/purchases/{id}/` | Purchase detail | `PurchaseDetailView`<br>model `Purchase`<br>(no serializer_class) |
| GET | `/api/purchases/analytics/` | Purchase analytics | `PurchaseAnalyticsView`<br>(no serializer_class) |
| GET, POST | `/api/purchases/purchase-orders/` | Purchase order list create | `PurchaseOrderListCreateView`<br>model `PurchaseOrder`<br>(no serializer_class) |
| GET, POST | `/api/purchases/purchase-returns/` | Purchase return list create | `PurchaseReturnListCreateView`<br>model `PurchaseReturn`<br>(no serializer_class) |
| GET, POST | `/api/purchases/vendors/` | Vendor list create | `VendorListCreateView`<br>model `Vendor`<br>ser `VendorSerializer`<br><small>fields: `id, name, contact_person, email, phone, country, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/purchases/purchase-orders/{id}/` | Purchase order detail | `PurchaseOrderDetailView`<br>model `PurchaseOrder`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/purchases/purchase-returns/{id}/` | Purchase return detail | `PurchaseReturnDetailView`<br>model `PurchaseReturn`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/purchases/vendors/{id}/` | Vendor detail | `VendorDetailView`<br>model `Vendor`<br>ser `VendorSerializer`<br><small>fields: `id, name, contact_person, email, phone, country, status, created_at, updated_at`</small> |

## Production & Manufacturing

`33` endpoints under **`/api/production/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/production/boms/` | Bom list create | `BomListCreateView`<br>model `Bom`<br>(no serializer_class) |
| GET, POST | `/api/production/dispatches/` | Dispatch list create | `DispatchListCreateView`<br>model `Dispatch`<br>(no serializer_class) |
| GET | `/api/production/finished-goods/` | Finished goods list | `FinishedGoodsListView`<br>ser `FinishedGoodsSerializer` |
| GET, POST | `/api/production/grns/` | Grn list create | `GoodsReceiptNoteListCreateView`<br>model `GoodsReceiptNote`<br>(no serializer_class) |
| GET, POST | `/api/production/inspections/` | Inspection list create | `QualityInspectionListCreateView`<br>model `QualityInspection`<br>(no serializer_class) |
| GET, POST | `/api/production/job-orders/` | Job order list create | `JobOrderListCreateView`<br>model `JobOrder`<br>(no serializer_class) |
| GET, POST | `/api/production/machines/` | Machine list create | `MachineListCreateView`<br>model `Machine`<br>ser `MachineSerializer`<br><small>fields: `id, name, code, machine_type, status, created_at, updated_at`</small> |
| GET | `/api/production/material-issues/` | Material issue list | `MaterialIssueSlipListView`<br>ser `MaterialIssueSlipSerializer` |
| GET | `/api/production/processes/` | Process list | `ProductionProcessListView`<br>ser `ProductionProcessSerializer` |
| GET, POST | `/api/production/requisitions/` | Requisition list create | `PurchaseRequisitionListCreateView`<br>model `PurchaseRequisition`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/production/boms/{id}/` | Bom detail | `BomDetailView`<br>model `Bom`<br>ser `BomSerializer`<br><small>fields: `id, name, product, product_name, version, status, items, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/production/dispatches/{id}/` | Dispatch detail | `DispatchDetailView`<br>model `Dispatch`<br>ser `DispatchSerializer`<br><small>fields: `id, dispatch_no, job_order, job_no, sales_order, sales_order_id_ref, customer, customer_name, delivery_note, delivery_note_id_ref, packing_note, label_printed, transport_mode, vehicle_number, driver_name, driver_phone, status, status_displa...`</small> |
| GET | `/api/production/finished-goods/{id}/` | Finished goods detail | `FinishedGoodsDetailView`<br>model `FinishedGoods`<br>ser `FinishedGoodsSerializer` |
| GET, PUT, PATCH, DELETE | `/api/production/grns/{id}/` | Grn detail | `GoodsReceiptNoteDetailView`<br>model `GoodsReceiptNote`<br>ser `GoodsReceiptNoteSerializer`<br><small>fields: `id, grn_no, purchase_order, purchase_order_id_ref, supplier, supplier_name, warehouse, warehouse_name, received_date, status, status_display, received_by, received_by_name, notes, items, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/production/inspections/{id}/` | Inspection detail | `QualityInspectionDetailView`<br>model `QualityInspection`<br>ser `QualityInspectionSerializer`<br><small>fields: `id, inspection_no, grn, grn_no, job_order, job_no, product, product_name, quantity, status, status_display, inspected_by, inspected_by_name, inspection_date, notes, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/production/job-orders/{id}/` | Job order detail | `JobOrderDetailView`<br>model `JobOrder`<br>ser `JobOrderSerializer`<br><small>fields: `id, job_no, sales_order, sales_order_id_ref, quotation, customer, customer_name, product, product_name, quantity, start_date, end_date, priority, status, status_display, progress, machine, machine_name, supervisor, supervisor_name, operator...`</small> |
| GET, PUT, PATCH, DELETE | `/api/production/machines/{id}/` | Machine detail | `MachineDetailView`<br>model `Machine`<br>ser `MachineSerializer`<br><small>fields: `id, name, code, machine_type, status, created_at, updated_at`</small> |
| GET | `/api/production/material-issues/{id}/` | Material issue detail | `MaterialIssueSlipDetailView`<br>ser `MaterialIssueSlipSerializer` |
| GET, DELETE | `/api/production/requisitions/{id}/` | Requisition detail | `PurchaseRequisitionDetailView`<br>model `PurchaseRequisition`<br>ser `PurchaseRequisitionSerializer` |
| POST | `/api/production/dispatches/{id}/mark-dispatched/` | Dispatch mark dispatched | `DispatchMarkDispatchedView`<br>(no serializer_class) |
| POST | `/api/production/grns/{id}/inspect/` | Grn inspect | `GoodsReceiptNoteInspectView`<br>(no serializer_class) |
| POST | `/api/production/grns/{id}/receive/` | Grn receive | `GoodsReceiptNoteReceiveView`<br>(no serializer_class) |
| POST | `/api/production/inspections/{id}/result/` | Inspection result | `QualityInspectionResultView`<br>(no serializer_class) |
| POST | `/api/production/job-orders/{id}/check-stock/` | Job order check stock | `JobOrderCheckStockView`<br>(no serializer_class) |
| POST | `/api/production/job-orders/{id}/create-requisition/` | Job order create requisition | `JobOrderCreateRequisitionView`<br>(no serializer_class) |
| POST | `/api/production/job-orders/{id}/dispatch/` | Job order dispatch | `JobOrderDispatchView`<br>(no serializer_class) |
| POST | `/api/production/job-orders/{id}/issue-material/` | Job order issue material | `JobOrderIssueMaterialView`<br>(no serializer_class) |
| POST | `/api/production/job-orders/{id}/qc/` | Job order qc | `JobOrderQcView`<br>(no serializer_class) |
| POST | `/api/production/job-orders/{id}/rework/` | Job order rework | `JobOrderReworkView`<br>(no serializer_class) |
| POST | `/api/production/job-orders/{id}/start/` | Job order start | `JobOrderStartProductionView`<br>(no serializer_class) |
| POST | `/api/production/processes/{id}/advance/` | Process advance | `ProductionProcessAdvanceView`<br>(no serializer_class) |
| POST | `/api/production/requisitions/{id}/approve/` | Requisition approve | `PurchaseRequisitionApproveView`<br>(no serializer_class) |
| POST | `/api/production/requisitions/{id}/reject/` | Requisition reject | `PurchaseRequisitionRejectView`<br>(no serializer_class) |

## Targets

`8` endpoints under **`/api/targets/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET | `/api/targets/` | Target list | `TargetListView`<br>ser `TargetWithAchievementSerializer` |
| GET, PUT, PATCH | `/api/targets/{id}/` | Target detail | `TargetDetailView`<br>ser `TargetSerializer`<br><small>fields: `id, employee, employee_name, employee_email, team, team_name, month, year, target_amount, achieved_amount, status, product, product_name, notes, created_at, updated_at`</small> |
| POST | `/api/targets/assign/` | Target assign | `TargetAssignView`<br>ser `TargetCreateSerializer`<br><small>fields: `id, employee, team, month, year, target_amount, achieved_amount, status, product, notes`</small> |
| GET | `/api/targets/export/` | Target export | `TargetExportView`<br>(no serializer_class) |
| GET | `/api/targets/leaderboard/` | Target leaderboard | `LeaderboardView`<br>(no serializer_class) |
| GET | `/api/targets/my/` | Target my | `MyTargetsView`<br>ser `TargetWithAchievementSerializer` |
| GET, POST | `/api/targets/teams/` | Team list | `TeamListCreateView`<br>model `Team`<br>ser `TeamSerializer`<br><small>fields: `id, name, team_lead, team_lead_name, members, members_count, target_revenue, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/targets/teams/{id}/` | Team detail | `TeamDetailView`<br>model `Team`<br>ser `TeamSerializer`<br><small>fields: `id, name, team_lead, team_lead_name, members, members_count, target_revenue, status, created_at, updated_at`</small> |

## Leaves

`15` endpoints under **`/api/leaves/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET | `/api/leaves/` | Leave list | `LeaveListView`<br>ser `LeaveSerializer` |
| GET | `/api/leaves/{id}/` | Leave detail | `LeaveDetailView`<br>ser `LeaveSerializer` |
| POST | `/api/leaves/admin-assign/` | Leave admin assign | `LeaveAdminAssignView`<br>ser `LeaveAdminAssignSerializer`<br><small>fields: `id, employee, leave_type, start_date, end_date, reason`</small> |
| GET, POST | `/api/leaves/allocations/` | Leave allocation list | `LeaveAllocationListCreateView`<br>model `LeaveAllocation`<br>ser `LeaveAllocationSerializer`<br><small>fields: `id, employee, employee_name, employee_email, leave_type, leave_type_name, allotted_days, year, created_at, updated_at`</small> |
| GET | `/api/leaves/my/` | Leave my | `MyLeaveListView`<br>ser `LeaveSerializer` |
| GET | `/api/leaves/pending-approvals/` | Leave pending approvals | `PendingApprovalsView`<br>ser `LeaveSerializer` |
| POST | `/api/leaves/request/` | Leave create | `LeaveCreateView`<br>ser `LeaveCreateSerializer`<br><small>fields: `id, leave_type, start_date, end_date, reason`</small> |
| GET, POST | `/api/leaves/types/` | Leave type list | `LeaveTypeListCreateView`<br>model `LeaveType`<br>ser `LeaveTypeSerializer`<br><small>fields: `id, name, days_allowed, is_active, created_at`</small> |
| GET, POST | `/api/leaves/workflow/` | Approval workflow list | `LeaveApprovalWorkflowListCreateView`<br>model `LeaveApprovalWorkflow`<br>ser `LeaveApprovalWorkflowSerializer`<br><small>fields: `id, employee, employee_name, employee_email, approver, approver_name, approver_email, priority, is_active, created_at`</small> |
| PATCH | `/api/leaves/{id}/approve/` | Leave approve | `LeaveApproveView`<br>(no serializer_class) |
| PATCH | `/api/leaves/{id}/reject/` | Leave reject | `LeaveRejectView`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/leaves/allocations/{id}/` | Leave allocation detail | `LeaveAllocationDetailView`<br>model `LeaveAllocation`<br>ser `LeaveAllocationSerializer`<br><small>fields: `id, employee, employee_name, employee_email, leave_type, leave_type_name, allotted_days, year, created_at, updated_at`</small> |
| GET | `/api/leaves/balance/{employee_id}/` | Leave balance | `LeaveBalanceView`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/leaves/types/{id}/` | Leave type detail | `LeaveTypeDetailView`<br>model `LeaveType`<br>ser `LeaveTypeSerializer`<br><small>fields: `id, name, days_allowed, is_active, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/leaves/workflow/{id}/` | Approval workflow detail | `LeaveApprovalWorkflowDetailView`<br>model `LeaveApprovalWorkflow`<br>ser `LeaveApprovalWorkflowSerializer`<br><small>fields: `id, employee, employee_name, employee_email, approver, approver_name, approver_email, priority, is_active, created_at`</small> |

## Notifications

`7` endpoints under **`/api/notifications/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET | `/api/notifications/` | Notification list | `NotificationListView`<br>ser `NotificationSerializer` |
| GET | `/api/notifications/{id}/` | Notification detail | `NotificationDetailView`<br>model `Notification`<br>ser `NotificationDetailSerializer` |
| GET | `/api/notifications/all/` | Notification all sent | `AllSentNotificationsView`<br>ser `NotificationSerializer` |
| PATCH | `/api/notifications/read-all/` | Notification read all | `MarkAllAsReadView`<br>(no serializer_class) |
| POST | `/api/notifications/send/` | Notification send | `SendNotificationView`<br>(no serializer_class) |
| GET | `/api/notifications/unread-count/` | Notification unread count | `UnreadCountView`<br>(no serializer_class) |
| PATCH | `/api/notifications/{id}/read/` | Notification mark read | `MarkAsReadView`<br>(no serializer_class) |

## Orders (Quotations & Work Orders)

`11` endpoints under **`/api/orders/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| POST | `/api/orders/` | Order create | `OrderCreateView`<br>model `Order`<br>ser `OrderCreateSerializer`<br><small>fields: `id, employee, dealer, client, order_date, notes, items`</small> |
| GET | `/api/orders/{id}/` | Order detail | `OrderDetailView`<br>model `Order`<br>ser `OrderSerializer` |
| GET | `/api/orders/export/` | Order export | `OrderExportView`<br>(no serializer_class) |
| GET | `/api/orders/list/` | Order list | `OrderListView`<br>ser `OrderSerializer` |
| GET | `/api/orders/my/` | Order my | `MyOrdersView`<br>ser `OrderSerializer` |
| GET, POST | `/api/orders/quotations/` | Quotation list | `QuotationListCreateView`<br>model `Quotation`<br>(no serializer_class) |
| PUT, PATCH | `/api/orders/{id}/status/` | Order status | `OrderStatusUpdateView`<br>model `Order`<br>ser `OrderStatusUpdateSerializer`<br><small>fields: `status`</small> |
| GET, PUT, PATCH, DELETE | `/api/orders/quotations/{id}/` | Quotation detail | `QuotationDetailView`<br>model `Quotation`<br>ser `QuotationSerializer`<br><small>fields: `id, quote_id, client, lead, lead_name, customer, customer_name, quote_date, valid_till, delivery_date, payment_terms, tax, tax_name, tax_percentage, gst_amount, shipping_charge, total_amount, discount, final_amount, notes, status, created_b...`</small> |
| POST | `/api/orders/quotations/{id}/approve/` | Quotation approve | `QuotationApproveView`<br>ser `QuotationSerializer`<br><small>fields: `id, quote_id, client, lead, lead_name, customer, customer_name, quote_date, valid_till, delivery_date, payment_terms, tax, tax_name, tax_percentage, gst_amount, shipping_charge, total_amount, discount, final_amount, notes, status, created_b...`</small> |
| POST | `/api/orders/quotations/{id}/reject/` | Quotation reject | `QuotationRejectView`<br>ser `QuotationSerializer`<br><small>fields: `id, quote_id, client, lead, lead_name, customer, customer_name, quote_date, valid_till, delivery_date, payment_terms, tax, tax_name, tax_percentage, gst_amount, shipping_charge, total_amount, discount, final_amount, notes, status, created_b...`</small> |
| POST | `/api/orders/quotations/{id}/send/` | Quotation send | `QuotationSendView`<br>ser `QuotationSerializer`<br><small>fields: `id, quote_id, client, lead, lead_name, customer, customer_name, quote_date, valid_till, delivery_date, payment_terms, tax, tax_name, tax_percentage, gst_amount, shipping_charge, total_amount, discount, final_amount, notes, status, created_b...`</small> |

## Reports

`14` endpoints under **`/api/reports/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET | `/api/reports/attendance/` | Report attendance | `AttendanceReportView`<br>(no serializer_class) |
| GET | `/api/reports/companies/` | Report companies | `CompanyReportView`<br>(no serializer_class) |
| GET | `/api/reports/compare/` | Report compare | `CompareEmployeesView`<br>(no serializer_class) |
| GET | `/api/reports/contacts/` | Report contacts | `ContactReportView`<br>(no serializer_class) |
| GET | `/api/reports/customer-analytics/` | Report customer analytics | `CustomerAnalyticsView`<br>(no serializer_class) |
| GET | `/api/reports/dashboard/` | Report dashboard | `DashboardView`<br>(no serializer_class) |
| GET | `/api/reports/deals/` | Report deals | `DealReportView`<br>(no serializer_class) |
| GET | `/api/reports/leads/` | Report leads | `LeadReportView`<br>(no serializer_class) |
| GET | `/api/reports/leaves/` | Report leaves | `LeaveReportView`<br>(no serializer_class) |
| GET | `/api/reports/performance/` | Report performance | `PerformanceOverviewView`<br>(no serializer_class) |
| GET | `/api/reports/projects/` | Report projects | `ProjectReportView`<br>(no serializer_class) |
| GET | `/api/reports/revenue/` | Report revenue | `RevenueReportView`<br>(no serializer_class) |
| GET | `/api/reports/tasks/` | Report tasks | `TaskReportView`<br>(no serializer_class) |
| GET | `/api/reports/weak-areas/` | Report weak areas | `WeakAreaAnalysisView`<br>(no serializer_class) |

## Pipeline (Leads)

`15` endpoints under **`/api/pipeline/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/pipeline/activities/` | Activity list | `ActivityListCreateView`<br>model `Activity`<br>ser `ActivitySerializer`<br><small>fields: `id, owner_name, deal_names, contact_names, company_names, created_by_name, title, activity_type, due_date, due_time, reminder, description, created_at, updated_at, owner, created_by, guests, deals, contacts, companies`</small> |
| GET, POST | `/api/pipeline/deals/` | Deal list | `DealListCreateView`<br>model `Deal`<br>ser `DealSerializer`<br><small>fields: `id, activities, owner_name, lead_name, contact_name, company_name, stage_name, pipeline_name, progress_name, name, value, progress, probability, status, period, period_value, due_date, expected_close_date, follow_up_date, tags, priority, de...`</small> |
| GET, POST | `/api/pipeline/leads/` | Lead list | `LeadListCreateView`<br>model `Lead`<br>ser `LeadSerializer`<br><small>fields: `id, owner_name, name, visible_to_names, first_name, last_name, lead_type, company_name, email, email_opt_out, phone, phone_2, fax, website, value, product_requirement, quantity, reviews, avatar, language, status, tags, description, visibili...`</small> |
| GET, POST | `/api/pipeline/opportunities/` | Opportunity list | `OpportunityListCreateView`<br>model `Opportunity`<br>ser `OpportunitySerializer`<br><small>fields: `id, owner_name, stage_name, opportunity_id, name, account, expected_value, stage, probability, expected_close_date, status, description, created_at, updated_at, owner`</small> |
| GET, POST | `/api/pipeline/pipelines/` | Pipeline list | `PipelineListCreateView`<br>model `Pipeline`<br>ser `PipelineSerializer`<br><small>fields: `id, stage_details, total_deal_value, deals_count, name, action, status, created_at, updated_at, stages`</small> |
| GET, POST | `/api/pipeline/stages/` | Pipeline stage list | `PipelineStageListCreateView`<br>model `PipelineStage`<br>ser `PipelineStageSerializer`<br><small>fields: `id, name, probability_default`</small> |
| GET, PUT, PATCH, DELETE | `/api/pipeline/activities/{id}/` | Activity detail | `ActivityDetailView`<br>model `Activity`<br>ser `ActivitySerializer`<br><small>fields: `id, owner_name, deal_names, contact_names, company_names, created_by_name, title, activity_type, due_date, due_time, reminder, description, created_at, updated_at, owner, created_by, guests, deals, contacts, companies`</small> |
| GET, PUT, PATCH, DELETE | `/api/pipeline/deals/{id}/` | Deal detail | `DealDetailView`<br>model `Deal`<br>ser `DealSerializer`<br><small>fields: `id, activities, owner_name, lead_name, contact_name, company_name, stage_name, pipeline_name, progress_name, name, value, progress, probability, status, period, period_value, due_date, expected_close_date, follow_up_date, tags, priority, de...`</small> |
| GET | `/api/pipeline/deals/pipeline/` | Deal pipeline | `DealPipelineView`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/pipeline/leads/{id}/` | Lead detail | `LeadDetailView`<br>model `Lead`<br>ser `LeadSerializer`<br><small>fields: `id, owner_name, name, visible_to_names, first_name, last_name, lead_type, company_name, email, email_opt_out, phone, phone_2, fax, website, value, product_requirement, quantity, reviews, avatar, language, status, tags, description, visibili...`</small> |
| GET, PUT, PATCH, DELETE | `/api/pipeline/opportunities/{id}/` | Opportunity detail | `OpportunityDetailView`<br>model `Opportunity`<br>ser `OpportunitySerializer`<br><small>fields: `id, owner_name, stage_name, opportunity_id, name, account, expected_value, stage, probability, expected_close_date, status, description, created_at, updated_at, owner`</small> |
| GET, PUT, PATCH, DELETE | `/api/pipeline/pipelines/{id}/` | Pipeline detail | `PipelineDetailView`<br>model `Pipeline`<br>ser `PipelineSerializer`<br><small>fields: `id, stage_details, total_deal_value, deals_count, name, action, status, created_at, updated_at, stages`</small> |
| GET, PUT, PATCH, DELETE | `/api/pipeline/stages/{id}/` | Pipeline stage detail | `PipelineStageDetailView`<br>model `PipelineStage`<br>ser `PipelineStageSerializer`<br><small>fields: `id, name, probability_default`</small> |
| GET, POST | `/api/pipeline/deals/{deal_pk}/activities/` | Deal activity list | `DealActivityListCreateView`<br>ser `DealActivitySerializer`<br><small>fields: `id, created_by_name, activity_type, description, attachment, created_at, deal, created_by`</small> |
| GET, PUT, PATCH, DELETE | `/api/pipeline/deals/{deal_pk}/activities/{id}/` | Deal activity detail | `DealActivityDetailView`<br>model `DealActivity`<br>ser `DealActivitySerializer`<br><small>fields: `id, created_by_name, activity_type, description, attachment, created_at, deal, created_by`</small> |

## Contacts

`7` endpoints under **`/api/contacts/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/contacts/companies/` | Company list | `CompanyListCreateView`<br>model `Company`<br>ser `CompanySerializer`<br><small>fields: `id, owner_name, name, email, email_opt_out, phone, phone_2, fax, website, reviews, avatar, tags, language, description, visibility, street_address, city, state, country, zipcode, facebook, skype, linkedin, twitter, whatsapp, instagram, stat...`</small> |
| GET, POST | `/api/contacts/contacts/` | Contact list | `ContactListCreateView`<br>model `Contact`<br>ser `ContactSerializer`<br><small>fields: `id, owner_name, company_name, name, visible_to_names, first_name, last_name, job_title, type, about, email, email_opt_out, phone, phone_2, fax, date_of_birth, reviews, avatar, tags, language, description, visibility, street_address, city, s...`</small> |
| GET, POST | `/api/contacts/messages/` | Contact message list | `ContactMessageListCreateView`<br>model `ContactMessage`<br>ser `ContactMessageSerializer`<br><small>fields: `id, name, phone, email, message, status, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/contacts/companies/{id}/` | Company detail | `CompanyDetailView`<br>model `Company`<br>ser `CompanySerializer`<br><small>fields: `id, owner_name, name, email, email_opt_out, phone, phone_2, fax, website, reviews, avatar, tags, language, description, visibility, street_address, city, state, country, zipcode, facebook, skype, linkedin, twitter, whatsapp, instagram, stat...`</small> |
| GET, PUT, PATCH, DELETE | `/api/contacts/contacts/{id}/` | Contact detail | `ContactDetailView`<br>model `Contact`<br>ser `ContactSerializer`<br><small>fields: `id, owner_name, company_name, name, visible_to_names, first_name, last_name, job_title, type, about, email, email_opt_out, phone, phone_2, fax, date_of_birth, reviews, avatar, tags, language, description, visibility, street_address, city, s...`</small> |
| GET, PUT, PATCH, DELETE | `/api/contacts/messages/{id}/` | Contact message detail | `ContactMessageDetailView`<br>model `ContactMessage`<br>ser `ContactMessageSerializer`<br><small>fields: `id, name, phone, email, message, status, created_at`</small> |
| PATCH | `/api/contacts/companies/{id}/toggle-status/` | Company toggle status | `CompanyToggleStatusView`<br>(no serializer_class) |

## Invoices

`5` endpoints under **`/api/invoices/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/invoices/invoices/` | Invoice list | `InvoiceListCreateView`<br>model `Invoice`<br>ser `InvoiceSerializer`<br><small>fields: `id, invoice_number, sales_order, sales_order_id_ref, delivery_note, delivery_note_id_ref, customer_name, customer_email, customer_address, billing_address, invoice_date, due_date, payment_method, transaction_id, subtotal, tax, tax_name, tax...`</small> |
| GET, POST | `/api/invoices/payments/` | Payment list | `PaymentListCreateView`<br>model `Payment`<br>ser `PaymentSerializer`<br><small>fields: `id, invoice, amount, method, payment_date, reference_number, notes, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/invoices/invoices/{id}/` | Invoice detail | `InvoiceDetailView`<br>model `Invoice`<br>ser `InvoiceSerializer`<br><small>fields: `id, invoice_number, sales_order, sales_order_id_ref, delivery_note, delivery_note_id_ref, customer_name, customer_email, customer_address, billing_address, invoice_date, due_date, payment_method, transaction_id, subtotal, tax, tax_name, tax...`</small> |
| GET, PUT, PATCH, DELETE | `/api/invoices/payments/{id}/` | Payment detail | `PaymentDetailView`<br>model `Payment`<br>ser `PaymentSerializer`<br><small>fields: `id, invoice, amount, method, payment_date, reference_number, notes, created_at`</small> |
| POST | `/api/invoices/invoices/{id}/mark-paid/` | Invoice mark paid | `InvoiceMarkPaidView`<br>ser `InvoiceSerializer`<br><small>fields: `id, invoice_number, sales_order, sales_order_id_ref, delivery_note, delivery_note_id_ref, customer_name, customer_email, customer_address, billing_address, invoice_date, due_date, payment_method, transaction_id, subtotal, tax, tax_name, tax...`</small> |

## Projects

`13` endpoints under **`/api/projects/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET | `/api/projects/analytics/` | Project analytics | `ProjectAnalyticsView`<br>(no serializer_class) |
| GET, POST | `/api/projects/milestones/` | Milestone list | `MilestoneListCreateView`<br>model `Milestone`<br>ser `MilestoneSerializer`<br><small>fields: `id, project_name, owner_name, milestone_id, name, date, notes, progress, status, created_at, updated_at, project, owner`</small> |
| GET, POST | `/api/projects/projects/` | Project list | `ProjectListCreateView`<br>model `Project`<br>ser `ProjectSerializer`<br><small>fields: `id, team_leader_name, responsible_person_names, name, project_id, project_type, description, client_name, category, project_timing, price, priority, status, start_date, due_date, budget, created_at, updated_at, team_leader, responsible_pers...`</small> |
| GET, POST | `/api/projects/resource-allocations/` | Resource allocation list | `ResourceAllocationListCreateView`<br>model `ResourceAllocation`<br>ser `ResourceAllocationSerializer`<br><small>fields: `id, resource_name, project_name, role, hours, allocated, availability, created_at, updated_at, resource, project`</small> |
| GET, POST | `/api/projects/tasks/` | Task list | `TaskListCreateView`<br>model `Task`<br>ser `TaskSerializer`<br><small>fields: `id, project_name, assignee_names, title, description, category, start_date, due_date, priority, status, tags, is_important, created_at, updated_at, project, assignees`</small> |
| GET, POST | `/api/projects/timesheets/` | Timesheet list | `TimesheetListCreateView`<br>model `Timesheet`<br>ser `TimesheetSerializer`<br><small>fields: `id, user_name, project_name, task_name, date, from_time, to_time, used_hours, description, status, created_at, updated_at, user, project, task`</small> |
| GET, POST | `/api/projects/todos/` | Todo list | `TodoItemListCreateView`<br>ser `TodoItemSerializer`<br><small>fields: `id, title, tag, priority, description, is_completed, status, created_at, updated_at, user, assignee`</small> |
| GET, PUT, PATCH, DELETE | `/api/projects/milestones/{id}/` | Milestone detail | `MilestoneDetailView`<br>model `Milestone`<br>ser `MilestoneSerializer`<br><small>fields: `id, project_name, owner_name, milestone_id, name, date, notes, progress, status, created_at, updated_at, project, owner`</small> |
| GET, PUT, PATCH, DELETE | `/api/projects/projects/{id}/` | Project detail | `ProjectDetailView`<br>model `Project`<br>ser `ProjectSerializer`<br><small>fields: `id, team_leader_name, responsible_person_names, name, project_id, project_type, description, client_name, category, project_timing, price, priority, status, start_date, due_date, budget, created_at, updated_at, team_leader, responsible_pers...`</small> |
| GET, PUT, PATCH, DELETE | `/api/projects/resource-allocations/{id}/` | Resource allocation detail | `ResourceAllocationDetailView`<br>model `ResourceAllocation`<br>ser `ResourceAllocationSerializer`<br><small>fields: `id, resource_name, project_name, role, hours, allocated, availability, created_at, updated_at, resource, project`</small> |
| GET, PUT, PATCH, DELETE | `/api/projects/tasks/{id}/` | Task detail | `TaskDetailView`<br>model `Task`<br>ser `TaskSerializer`<br><small>fields: `id, project_name, assignee_names, title, description, category, start_date, due_date, priority, status, tags, is_important, created_at, updated_at, project, assignees`</small> |
| GET, PUT, PATCH, DELETE | `/api/projects/timesheets/{id}/` | Timesheet detail | `TimesheetDetailView`<br>model `Timesheet`<br>ser `TimesheetSerializer`<br><small>fields: `id, user_name, project_name, task_name, date, from_time, to_time, used_hours, description, status, created_at, updated_at, user, project, task`</small> |
| GET, PUT, PATCH, DELETE | `/api/projects/todos/{id}/` | Todo detail | `TodoItemDetailView`<br>ser `TodoItemSerializer`<br><small>fields: `id, title, tag, priority, description, is_completed, status, created_at, updated_at, user, assignee`</small> |

## Contracts

`2` endpoints under **`/api/contracts/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/contracts/contracts/` | Contract list | `ContractListCreateView`<br>model `Contract`<br>ser `ContractSerializer`<br><small>fields: `id, created_by_name, title, client_name, contract_type, value, start_date, end_date, status, description, attachment, signature, created_at, updated_at, created_by`</small> |
| GET, PUT, PATCH, DELETE | `/api/contracts/contracts/{id}/` | Contract detail | `ContractDetailView`<br>model `Contract`<br>ser `ContractSerializer`<br><small>fields: `id, created_by_name, title, client_name, contract_type, value, start_date, end_date, status, description, attachment, signature, created_at, updated_at, created_by`</small> |

## Email Marketing

`7` endpoints under **`/api/email-marketing/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/email-marketing/campaigns/` | Email campaign list | `EmailCampaignListCreateView`<br>model `EmailCampaign`<br>ser `EmailCampaignSerializer`<br><small>fields: `id, created_by_name, name, campaign_type, subject, body, recipient_type, recipient_ids, recipient_pin_code, recipient_territory, period, start_date, end_date, description, attachment, status, sent_count, opened_count, clicked_count, created...`</small> |
| GET | `/api/email-marketing/engagement/` | Email engagement | `EmailEngagementReportView`<br>model `EmailCampaign`<br>ser `EmailEngagementSerializer` |
| GET, POST | `/api/email-marketing/subscriber-lists/` | Subscriber list | `SubscriberListListCreateView`<br>model `SubscriberList`<br>ser `SubscriberListSerializer`<br><small>fields: `id, name, total_contacts, active_subscribers, bounce_rate, last_campaign_date, created_at, updated_at`</small> |
| GET, POST | `/api/email-marketing/templates/` | Email template list | `EmailTemplateListCreateView`<br>model `EmailTemplate`<br>ser `EmailTemplateSerializer`<br><small>fields: `id, name, subject, body, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/email-marketing/campaigns/{id}/` | Email campaign detail | `EmailCampaignDetailView`<br>model `EmailCampaign`<br>ser `EmailCampaignSerializer`<br><small>fields: `id, created_by_name, name, campaign_type, subject, body, recipient_type, recipient_ids, recipient_pin_code, recipient_territory, period, start_date, end_date, description, attachment, status, sent_count, opened_count, clicked_count, created...`</small> |
| GET, PUT, PATCH, DELETE | `/api/email-marketing/subscriber-lists/{id}/` | Subscriber list detail | `SubscriberListDetailView`<br>model `SubscriberList`<br>ser `SubscriberListSerializer`<br><small>fields: `id, name, total_contacts, active_subscribers, bounce_rate, last_campaign_date, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/email-marketing/templates/{id}/` | Email template detail | `EmailTemplateDetailView`<br>model `EmailTemplate`<br>ser `EmailTemplateSerializer`<br><small>fields: `id, name, subject, body, created_at, updated_at`</small> |

## Chat

`5` endpoints under **`/api/chat/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/chat/conversations/` | Conversation list | `ConversationListCreateView`<br>ser `ConversationSerializer`<br><small>fields: `id, participant_names, last_message_preview, last_message, last_message_at, created_at, updated_at, participants`</small> |
| GET | `/api/chat/unread-count/` | Chat unread count | `UnreadCountView`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/chat/conversations/{id}/` | Conversation detail | `ConversationDetailView`<br>model `Conversation`<br>ser `ConversationSerializer`<br><small>fields: `id, participant_names, last_message_preview, last_message, last_message_at, created_at, updated_at, participants`</small> |
| GET, POST | `/api/chat/conversations/{conversation_pk}/messages/` | Message list | `MessageListCreateView`<br>ser `MessageSerializer`<br><small>fields: `id, sender_name, receiver_name, message, attachment, is_read, created_at, conversation, sender, receiver`</small> |
| GET, PUT, PATCH, DELETE | `/api/chat/conversations/{conversation_pk}/messages/{id}/` | Message detail | `MessageDetailView`<br>ser `MessageSerializer`<br><small>fields: `id, sender_name, receiver_name, message, attachment, is_read, created_at, conversation, sender, receiver`</small> |

## Tickets / Support

`4` endpoints under **`/api/tickets/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/tickets/tickets/` | Ticket list | `TicketListCreateView`<br>model `Ticket`<br>ser `TicketSerializer`<br><small>fields: `id, customer_name, assigned_to_name, replies, ticket_id, subject, description, priority, status, category, due_date, attachment, created_at, updated_at, customer, assigned_to`</small> |
| GET, PUT, PATCH, DELETE | `/api/tickets/tickets/{id}/` | Ticket detail | `TicketDetailView`<br>model `Ticket`<br>ser `TicketSerializer`<br><small>fields: `id, customer_name, assigned_to_name, replies, ticket_id, subject, description, priority, status, category, due_date, attachment, created_at, updated_at, customer, assigned_to`</small> |
| GET, POST | `/api/tickets/tickets/{ticket_pk}/replies/` | Ticket reply list | `TicketReplyListCreateView`<br>ser `TicketReplySerializer`<br><small>fields: `id, message, attachment, created_at, ticket, user`</small> |
| GET, PUT, PATCH, DELETE | `/api/tickets/tickets/{ticket_pk}/replies/{id}/` | Ticket reply detail | `TicketReplyDetailView`<br>ser `TicketReplySerializer`<br><small>fields: `id, message, attachment, created_at, ticket, user`</small> |

## Blog

`8` endpoints under **`/api/blog/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/blog/categories/` | Blog category list | `BlogCategoryListCreateView`<br>model `BlogCategory`<br>ser `BlogCategorySerializer`<br><small>fields: `id, name, slug, description`</small> |
| GET, POST | `/api/blog/comments/` | Blog comment list | `BlogCommentListCreateView`<br>model `BlogComment`<br>ser `BlogCommentSerializer`<br><small>fields: `id, post, name, email, content, is_approved, created_at`</small> |
| GET, POST | `/api/blog/posts/` | Blog post list | `BlogPostListCreateView`<br>model `BlogPost`<br>ser `BlogPostSerializer`<br><small>fields: `id, title, slug, content, excerpt, featured_image, author, author_name, category, category_name, tags, status, published_at, created_at, updated_at`</small> |
| GET, POST | `/api/blog/tags/` | Blog tag list | `BlogTagListCreateView`<br>model `BlogTag`<br>ser `BlogTagSerializer`<br><small>fields: `id, name, slug, status, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/blog/categories/{id}/` | Blog category detail | `BlogCategoryDetailView`<br>model `BlogCategory`<br>ser `BlogCategorySerializer`<br><small>fields: `id, name, slug, description`</small> |
| GET, PUT, PATCH, DELETE | `/api/blog/comments/{id}/` | Blog comment detail | `BlogCommentDetailView`<br>model `BlogComment`<br>ser `BlogCommentSerializer`<br><small>fields: `id, post, name, email, content, is_approved, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/blog/posts/{id}/` | Blog post detail | `BlogPostDetailView`<br>model `BlogPost`<br>ser `BlogPostSerializer`<br><small>fields: `id, title, slug, content, excerpt, featured_image, author, author_name, category, category_name, tags, status, published_at, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/blog/tags/{id}/` | Blog tag detail | `BlogTagDetailView`<br>model `BlogTag`<br>ser `BlogTagSerializer`<br><small>fields: `id, name, slug, status, created_at`</small> |

## Masters - Configuration

`14` endpoints under **`/api/config/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/config/call-logs/` | Call log list | `CallLogListCreateView`<br>model `CallLog`<br>ser `CallLogSerializer`<br><small>fields: `id, created_by_name, name, phone, call_type, duration, date_time, notes, created_at, created_by`</small> |
| GET, POST | `/api/config/call-reasons/` | Call reason list | `CallReasonListCreateView`<br>model `CallReason`<br>ser `CallReasonSerializer`<br><small>fields: `id, title, status, created_at`</small> |
| GET, POST | `/api/config/contact-stages/` | Contact stage list | `ContactStageListCreateView`<br>model `ContactStage`<br>ser `ContactStageSerializer`<br><small>fields: `id, title, status, created_at`</small> |
| GET, POST | `/api/config/currencies/` | Currency list | `CurrencyListCreateView`<br>model `Currency`<br>ser `CurrencySerializer`<br><small>fields: `id, name, code, symbol, exchange_rate, is_active`</small> |
| GET, POST | `/api/config/industries/` | Industry list | `IndustryListCreateView`<br>model `Industry`<br>ser `IndustrySerializer`<br><small>fields: `id, name, is_active`</small> |
| GET, POST | `/api/config/lost-reasons/` | Lost reason list | `LostReasonListCreateView`<br>model `LostReason`<br>ser `LostReasonSerializer`<br><small>fields: `id, title, status, created_at`</small> |
| GET, POST | `/api/config/sources/` | Source list | `SourceListCreateView`<br>model `Source`<br>ser `SourceSerializer`<br><small>fields: `id, name, source_type, is_active`</small> |
| GET, PUT, PATCH, DELETE | `/api/config/call-logs/{id}/` | Call log detail | `CallLogDetailView`<br>model `CallLog`<br>ser `CallLogSerializer`<br><small>fields: `id, created_by_name, name, phone, call_type, duration, date_time, notes, created_at, created_by`</small> |
| GET, PUT, PATCH, DELETE | `/api/config/call-reasons/{id}/` | Call reason detail | `CallReasonDetailView`<br>model `CallReason`<br>ser `CallReasonSerializer`<br><small>fields: `id, title, status, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/config/contact-stages/{id}/` | Contact stage detail | `ContactStageDetailView`<br>model `ContactStage`<br>ser `ContactStageSerializer`<br><small>fields: `id, title, status, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/config/currencies/{id}/` | Currency detail | `CurrencyDetailView`<br>model `Currency`<br>ser `CurrencySerializer`<br><small>fields: `id, name, code, symbol, exchange_rate, is_active`</small> |
| GET, PUT, PATCH, DELETE | `/api/config/industries/{id}/` | Industry detail | `IndustryDetailView`<br>model `Industry`<br>ser `IndustrySerializer`<br><small>fields: `id, name, is_active`</small> |
| GET, PUT, PATCH, DELETE | `/api/config/lost-reasons/{id}/` | Lost reason detail | `LostReasonDetailView`<br>model `LostReason`<br>ser `LostReasonSerializer`<br><small>fields: `id, title, status, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/config/sources/{id}/` | Source detail | `SourceDetailView`<br>model `Source`<br>ser `SourceSerializer`<br><small>fields: `id, name, source_type, is_active`</small> |

## Subscriptions

`9` endpoints under **`/api/subscriptions/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/subscriptions/addons/` | Addon list | `MembershipAddonListCreateView`<br>model `MembershipAddon`<br>(no serializer_class) |
| GET, POST | `/api/subscriptions/plans/` | Plan list | `MembershipPlanListCreateView`<br>model `MembershipPlan`<br>(no serializer_class) |
| GET, POST | `/api/subscriptions/subscriptions/` | Subscription list | `SubscriptionListCreateView`<br>model `Subscription`<br>(no serializer_class) |
| GET, POST | `/api/subscriptions/transactions/` | Transaction list | `SubscriptionTransactionListCreateView`<br>model `SubscriptionTransaction`<br>ser `SubscriptionTransactionSerializer`<br><small>fields: `id, amount, payment_method, transaction_id, status, created_at, subscription`</small> |
| GET, PUT, PATCH, DELETE | `/api/subscriptions/addons/{id}/` | Addon detail | `MembershipAddonDetailView`<br>model `MembershipAddon`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/subscriptions/plans/{id}/` | Plan detail | `MembershipPlanDetailView`<br>model `MembershipPlan`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/subscriptions/subscriptions/{id}/` | Subscription detail | `SubscriptionDetailView`<br>model `Subscription`<br>ser `SubscriptionSerializer`<br><small>fields: `id, user_name, plan_name, start_date, end_date, status, auto_renew, created_at, user, plan`</small> |
| GET | `/api/subscriptions/subscriptions/my/` | Subscription my | `MySubscriptionView`<br>ser `SubscriptionSerializer` |
| GET, PUT, PATCH, DELETE | `/api/subscriptions/transactions/{id}/` | Transaction detail | `SubscriptionTransactionDetailView`<br>model `SubscriptionTransaction`<br>ser `SubscriptionTransactionSerializer`<br><small>fields: `id, amount, payment_method, transaction_id, status, created_at, subscription`</small> |

## Marketing

`4` endpoints under **`/api/marketing/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/marketing/campaigns/` | Campaign list | `CampaignListCreateView`<br>model `Campaign`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/marketing/campaigns/{id}/` | Campaign detail | `CampaignDetailView`<br>model `Campaign`<br>ser `CampaignDetailSerializer`<br><small>fields: `id, type, name, subject, title, message, content, recipient_filter, status, scheduled_at, sent_at, deal_value, currency, period, period_value, target_audience, target_audience_details, description, attachment, stats_sent_count, stats_opened...`</small> |
| PATCH | `/api/marketing/campaigns/{id}/archive/` | Campaign archive | `CampaignArchiveView`<br>(no serializer_class) |
| POST | `/api/marketing/campaigns/{id}/send/` | Campaign send | `CampaignSendView`<br>(no serializer_class) |

## Finance

`27` endpoints under **`/api/finance/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/finance/bank-accounts/` | Bankaccountlistcreate | `BankAccountListCreateView`<br>model `BankAccount`<br>ser `BankAccountSerializer`<br><small>fields: `id, bank_name, account_holder_name, account_number, ifsc_code, branch, account_type, is_default, is_active, created_at`</small> |
| GET, POST | `/api/finance/budgets/` | Budgetlistcreate | `BudgetListCreateView`<br>model `Budget`<br>ser `BudgetSerializer`<br><small>fields: `id, budget_id, period, category, category_name, budget, spent, remaining, usage_percent, created_at, updated_at`</small> |
| GET, POST | `/api/finance/cashflows/` | Cashflowlistcreate | `CashflowListCreateView`<br>model `Cashflow`<br>ser `CashflowSerializer`<br><small>fields: `id, ref_id, bank, bank_name, type, payment_method, amount, date, status, created_at, updated_at`</small> |
| GET, POST | `/api/finance/expense-categories/` | Expensecategorylistcreate | `ExpenseCategoryListCreateView`<br>model `ExpenseCategory`<br>ser `ExpenseCategorySerializer`<br><small>fields: `id, name, slug, description, status, created_at, updated_at`</small> |
| GET, POST | `/api/finance/expenses/` | Expenselistcreate | `ExpenseListCreateView`<br>model `Expense`<br>ser `ExpenseSerializer`<br><small>fields: `id, expense_id, name, category, category_name, amount, payment_method, date, description, status, created_at, updated_at`</small> |
| GET, POST | `/api/finance/income-categories/` | Incomecategorylistcreate | `IncomeCategoryListCreateView`<br>model `IncomeCategory`<br>ser `IncomeCategorySerializer`<br><small>fields: `id, name, slug, description, status, created_at, updated_at`</small> |
| GET, POST | `/api/finance/incomes/` | Incomelistcreate | `IncomeListCreateView`<br>model `Income`<br>ser `IncomeSerializer`<br><small>fields: `id, income_id, party_name, category, category_name, amount, payment_method, date, status, created_at, updated_at`</small> |
| GET, POST | `/api/finance/payments/` | Paymentlistcreate | `PaymentListCreateView`<br>model `Payment`<br>ser `PaymentSerializer`<br><small>fields: `id, payment_id, payee, bank, bank_name, payment_method, amount, date, status, created_at, updated_at`</small> |
| GET, POST | `/api/finance/payrolls/` | Payrolllistcreate | `PayrollListCreateView`<br>model `Payroll`<br>ser `PayrollSerializer`<br><small>fields: `id, payroll_id, employee, employee_name, designation, designation_name, department, department_name, payroll_month, payment_date, basic_salary, hra, conveyance, bonus, other_allowance, pf, professional_tax, tds, other_deductions, total_earn...`</small> |
| GET, POST | `/api/finance/purchase-taxes/` | Purchasetaxlistcreate | `PurchaseTaxListCreateView`<br>model `PurchaseTax`<br>ser `PurchaseTaxSerializer`<br><small>fields: `id, bill_id, supplier, tax_type, tax_type_name, tax_amount, payment_method, date, status, created_at, updated_at`</small> |
| GET, POST | `/api/finance/taxes/` | Taxlistcreate | `TaxListCreateView`<br>model `Tax`<br>ser `TaxSerializer`<br><small>fields: `id, tax_id, name, rate, status, applied_to, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/finance/bank-accounts/{id}/` | Bankaccountdetail | `BankAccountDetailView`<br>model `BankAccount`<br>ser `BankAccountSerializer`<br><small>fields: `id, bank_name, account_holder_name, account_number, ifsc_code, branch, account_type, is_default, is_active, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/finance/budgets/{id}/` | Budgetdetail | `BudgetDetailView`<br>model `Budget`<br>ser `BudgetSerializer`<br><small>fields: `id, budget_id, period, category, category_name, budget, spent, remaining, usage_percent, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/finance/cashflows/{id}/` | Cashflowdetail | `CashflowDetailView`<br>model `Cashflow`<br>ser `CashflowSerializer`<br><small>fields: `id, ref_id, bank, bank_name, type, payment_method, amount, date, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/finance/expense-categories/{id}/` | Expensecategorydetail | `ExpenseCategoryDetailView`<br>model `ExpenseCategory`<br>ser `ExpenseCategorySerializer`<br><small>fields: `id, name, slug, description, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/finance/expenses/{id}/` | Expensedetail | `ExpenseDetailView`<br>model `Expense`<br>ser `ExpenseSerializer`<br><small>fields: `id, expense_id, name, category, category_name, amount, payment_method, date, description, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/finance/income-categories/{id}/` | Incomecategorydetail | `IncomeCategoryDetailView`<br>model `IncomeCategory`<br>ser `IncomeCategorySerializer`<br><small>fields: `id, name, slug, description, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/finance/incomes/{id}/` | Incomedetail | `IncomeDetailView`<br>model `Income`<br>ser `IncomeSerializer`<br><small>fields: `id, income_id, party_name, category, category_name, amount, payment_method, date, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/finance/payments/{id}/` | Paymentdetail | `PaymentDetailView`<br>model `Payment`<br>ser `PaymentSerializer`<br><small>fields: `id, payment_id, payee, bank, bank_name, payment_method, amount, date, status, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/finance/payrolls/{id}/` | Payrolldetail | `PayrollDetailView`<br>model `Payroll`<br>ser `PayrollSerializer`<br><small>fields: `id, payroll_id, employee, employee_name, designation, designation_name, department, department_name, payroll_month, payment_date, basic_salary, hra, conveyance, bonus, other_allowance, pf, professional_tax, tds, other_deductions, total_earn...`</small> |
| GET, PUT, PATCH, DELETE | `/api/finance/purchase-taxes/{id}/` | Purchasetaxdetail | `PurchaseTaxDetailView`<br>model `PurchaseTax`<br>ser `PurchaseTaxSerializer`<br><small>fields: `id, bill_id, supplier, tax_type, tax_type_name, tax_amount, payment_method, date, status, created_at, updated_at`</small> |
| GET | `/api/finance/reports/expense-summary/` | Expensesummary | `ExpenseSummaryView`<br>(no serializer_class) |
| GET | `/api/finance/reports/income-summary/` | Incomesummary | `IncomeSummaryView`<br>(no serializer_class) |
| GET | `/api/finance/reports/income-vs-expense/` | Incomevsexpense | `IncomeVsExpenseView`<br>(no serializer_class) |
| GET | `/api/finance/reports/profit-loss/` | Profitloss | `ProfitLossView`<br>(no serializer_class) |
| GET | `/api/finance/reports/tax-summary/` | Taxsummary | `TaxSummaryView`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/finance/taxes/{id}/` | Taxdetail | `TaxDetailView`<br>model `Tax`<br>ser `TaxSerializer`<br><small>fields: `id, tax_id, name, rate, status, applied_to, created_at, updated_at`</small> |

## Estimations

`4` endpoints under **`/api/estimations/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/estimations/estimations/` | Estimation list | `EstimationListCreateView`<br>model `Estimation`<br>ser `EstimationSerializer`<br><small>fields: `id, estimation_number, title, customer_name, customer_email, customer_phone, valid_until, subtotal, tax, tax_name, tax_percentage, tax_amount, discount_percentage, discount_amount, total, status, notes, created_by, created_at, updated_at, i...`</small> |
| GET, POST | `/api/estimations/proposals/` | Proposal list | `ProposalListCreateView`<br>model `Proposal`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/estimations/estimations/{id}/` | Estimation detail | `EstimationDetailView`<br>model `Estimation`<br>ser `EstimationSerializer`<br><small>fields: `id, estimation_number, title, customer_name, customer_email, customer_phone, valid_until, subtotal, tax, tax_name, tax_percentage, tax_amount, discount_percentage, discount_amount, total, status, notes, created_by, created_at, updated_at, i...`</small> |
| GET, PUT, PATCH, DELETE | `/api/estimations/proposals/{id}/` | Proposal detail | `ProposalDetailView`<br>model `Proposal`<br>ser `ProposalSerializer`<br><small>fields: `id, proposal_number, title, customer_name, customer_email, customer_phone, content, version, status, valid_until, total_amount, created_by, created_at, updated_at`</small> |

## Settings Configuration

`27` endpoints under **`/api/settings/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, PUT | `/api/settings/appearance/` | Appearancesetting | `AppearanceSettingView`<br>(no serializer_class) |
| GET, POST | `/api/settings/countries/` | Countrylistcreate | `CountryListCreateView`<br>model `Country`<br>ser `CountrySerializer`<br><small>fields: `id, name, code, is_active, created_at`</small> |
| GET, POST | `/api/settings/custom-fields/` | Customfieldlistcreate | `CustomFieldListCreateView`<br>model `CustomField`<br>ser `CustomFieldSerializer`<br><small>fields: `id, model_name, field_name, field_type, options, is_required, is_active, created_at`</small> |
| GET, POST | `/api/settings/departments/` | Departmentlistcreate | `DepartmentListCreateView`<br>model `Department`<br>ser `DepartmentSerializer`<br><small>fields: `id, name, department_head, department_head_name, description, status, employee_count, created_at`</small> |
| GET, POST | `/api/settings/designations/` | Designationlistcreate | `DesignationListCreateView`<br>model `Designation`<br>ser `DesignationSerializer`<br><small>fields: `id, name, department, department_name, status, employee_count, created_at`</small> |
| GET, PUT, PATCH | `/api/settings/email-settings/` | Emailsetting | `EmailSettingView`<br>ser `EmailSettingSerializer`<br><small>fields: `id, mail_driver, host, port, encryption, username, password, from_email, from_name`</small> |
| GET, POST | `/api/settings/gdpr/` | Gdprconsentlistcreate | `GDPRConsentListCreateView`<br>model `GDPRConsent`<br>ser `GDPRConsentSerializer`<br><small>fields: `id, user_email, consent_type, is_accepted, accepted_at, ip_address, user`</small> |
| GET, PUT, PATCH | `/api/settings/invoice-settings/` | Invoicesetting | `InvoiceSettingView`<br>ser `InvoiceSettingSerializer`<br><small>fields: `id, prefix, next_number, default_terms, default_payment_method, show_tax, show_discount, footer_text`</small> |
| GET, POST | `/api/settings/languages/` | Languagesettinglistcreate | `LanguageSettingListCreateView`<br>model `LanguageSetting`<br>ser `LanguageSettingSerializer`<br><small>fields: `id, code, name, is_default, is_active`</small> |
| GET, PUT, PATCH | `/api/settings/localization/` | Localizationsetting | `LocalizationSettingView`<br>ser `LocalizationSettingSerializer`<br><small>fields: `id, timezone, date_format, time_format, currency_symbol, decimal_separator, thousand_separator`</small> |
| GET, POST | `/api/settings/notification-settings/` | Notificationsettinglistcreate | `NotificationSettingListCreateView`<br>model `NotificationSetting`<br>ser `NotificationSettingSerializer`<br><small>fields: `id, module, email_enabled, sms_enabled, push_enabled, in_app_enabled, updated_at`</small> |
| GET, POST | `/api/settings/prefixes/` | Prefixsettinglistcreate | `PrefixSettingListCreateView`<br>model `PrefixSetting`<br>ser `PrefixSettingSerializer`<br><small>fields: `id, module, prefix, next_number, separator, example`</small> |
| GET, POST | `/api/settings/printers/` | Printersettinglistcreate | `PrinterSettingListCreateView`<br>model `PrinterSetting`<br>ser `PrinterSettingSerializer`<br><small>fields: `id, name, printer_type, is_default, is_active, created_at`</small> |
| GET, PUT, PATCH | `/api/settings/security-settings/` | Securitysetting | `SecuritySettingView`<br>ser `SecuritySettingSerializer`<br><small>fields: `id, password_min_length, require_special_char, require_number, max_login_attempts, session_timeout_minutes, two_factor_required`</small> |
| GET, POST | `/api/settings/sms-gateways/` | Smsgatewaylistcreate | `SmsGatewayListCreateView`<br>model `SmsGateway`<br>ser `SmsGatewaySerializer`<br><small>fields: `id, name, api_key, api_secret, sender_id, is_default, is_active, created_at`</small> |
| GET, PUT, PATCH | `/api/settings/storage-settings/` | Storagesetting | `StorageSettingView`<br>ser `StorageSettingSerializer`<br><small>fields: `id, driver, aws_access_key, aws_secret_key, bucket, region, base_url`</small> |
| GET, PUT, PATCH | `/api/settings/system-update/` | Systemupdate | `SystemUpdateView`<br>ser `SystemUpdateSerializer`<br><small>fields: `id, purchase_key, version, is_updated, last_checked_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/settings/countries/{id}/` | Countrydetail | `CountryDetailView`<br>model `Country`<br>ser `CountrySerializer`<br><small>fields: `id, name, code, is_active, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/settings/custom-fields/{id}/` | Customfielddetail | `CustomFieldDetailView`<br>model `CustomField`<br>ser `CustomFieldSerializer`<br><small>fields: `id, model_name, field_name, field_type, options, is_required, is_active, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/settings/departments/{id}/` | Departmentdetail | `DepartmentDetailView`<br>model `Department`<br>ser `DepartmentSerializer`<br><small>fields: `id, name, department_head, department_head_name, description, status, employee_count, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/settings/designations/{id}/` | Designationdetail | `DesignationDetailView`<br>model `Designation`<br>ser `DesignationSerializer`<br><small>fields: `id, name, department, department_name, status, employee_count, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/settings/languages/{id}/` | Languagesettingdetail | `LanguageSettingDetailView`<br>model `LanguageSetting`<br>ser `LanguageSettingSerializer`<br><small>fields: `id, code, name, is_default, is_active`</small> |
| GET, PUT, PATCH, DELETE | `/api/settings/notification-settings/{id}/` | Notificationsettingdetail | `NotificationSettingDetailView`<br>model `NotificationSetting`<br>ser `NotificationSettingSerializer`<br><small>fields: `id, module, email_enabled, sms_enabled, push_enabled, in_app_enabled, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/settings/prefixes/{id}/` | Prefixsettingdetail | `PrefixSettingDetailView`<br>model `PrefixSetting`<br>ser `PrefixSettingSerializer`<br><small>fields: `id, module, prefix, next_number, separator, example`</small> |
| GET, PUT, PATCH, DELETE | `/api/settings/printers/{id}/` | Printersettingdetail | `PrinterSettingDetailView`<br>model `PrinterSetting`<br>ser `PrinterSettingSerializer`<br><small>fields: `id, name, printer_type, is_default, is_active, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/settings/sms-gateways/{id}/` | Smsgatewaydetail | `SmsGatewayDetailView`<br>model `SmsGateway`<br>ser `SmsGatewaySerializer`<br><small>fields: `id, name, api_key, api_secret, sender_id, is_default, is_active, created_at`</small> |
| PATCH | `/api/settings/prefixes/{id}/next/` | Prefixsettingnextnumber | `PrefixSettingNextNumberView`<br>(no serializer_class) |

## Content Management

`13` endpoints under **`/api/content/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/content/faq/` | Faqlistcreate | `FAQListCreateView`<br>model `FAQ`<br>(no serializer_class) |
| GET, POST | `/api/content/files/` | Filemanagerfilelistcreate | `FileManagerFileListCreateView`<br>model `FileManagerFile`<br>ser `FileManagerFileSerializer`<br><small>fields: `id, name, file, file_url, folder, file_type, file_size, uploaded_by, uploaded_by_name, uploaded_at`</small> |
| GET, POST | `/api/content/notes/` | Notelistcreate | `NoteListCreateView`<br>ser `NoteSerializer`<br><small>fields: `id, title, content, user, is_pinned, color, created_at, updated_at`</small> |
| GET, POST | `/api/content/pages/` | Staticpagelistcreate | `StaticPageListCreateView`<br>model `StaticPage`<br>(no serializer_class) |
| GET, POST | `/api/content/social-feed/` | Socialfeedpostlistcreate | `SocialFeedPostListCreateView`<br>model `SocialFeedPost`<br>(no serializer_class) |
| GET, POST | `/api/content/testimonials/` | Testimoniallistcreate | `TestimonialListCreateView`<br>model `Testimonial`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/content/faq/{id}/` | Faqdetail | `FAQDetailView`<br>model `FAQ`<br>ser `FAQSerializer`<br><small>fields: `id, question, answer, category, order, is_active, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/content/files/{id}/` | Filemanagerfiledetail | `FileManagerFileDetailView`<br>model `FileManagerFile`<br>ser `FileManagerFileSerializer`<br><small>fields: `id, name, file, file_url, folder, file_type, file_size, uploaded_by, uploaded_by_name, uploaded_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/content/notes/{id}/` | Notedetail | `NoteDetailView`<br>ser `NoteSerializer`<br><small>fields: `id, title, content, user, is_pinned, color, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/content/pages/{id}/` | Staticpagedetail | `StaticPageDetailView`<br>model `StaticPage`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/content/social-feed/{id}/` | Socialfeedpostdetail | `SocialFeedPostDetailView`<br>model `SocialFeedPost`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/content/testimonials/{id}/` | Testimonialdetail | `TestimonialDetailView`<br>model `Testimonial`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/content/pages/by-slug/{slug}/` | Staticpagedetail | `StaticPageDetailView`<br>model `StaticPage`<br>(no serializer_class) |

## System Admin

`12` endpoints under **`/api/system/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/system/backups/` | Backuploglistcreate | `BackupLogListCreateView`<br>model `BackupLog`<br>(no serializer_class) |
| GET, POST | `/api/system/banned-ips/` | Bannediplistcreate | `BannedIPListCreateView`<br>model `BannedIP`<br>(no serializer_class) |
| POST | `/api/system/clear-cache/` | Clearcache | `ClearCacheView`<br>(no serializer_class) |
| GET, POST | `/api/system/connected-apps/` | Connectedapplistcreate | `ConnectedAppListCreateView`<br>model `ConnectedApp`<br>(no serializer_class) |
| GET, POST | `/api/system/cron-jobs/` | Cronjoblistcreate | `CronJobListCreateView`<br>model `CronJob`<br>(no serializer_class) |
| GET | `/api/system/info/` | Systeminfo | `SystemInfoView`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/system/backups/{id}/` | Backuplogdetail | `BackupLogDetailView`<br>model `BackupLog`<br>ser `BackupLogSerializer`<br><small>fields: `id, created_by_name, filename, file_size, backup_type, status, started_at, completed_at, notes, created_by`</small> |
| POST | `/api/system/backups/run/` | Backupnow | `BackupNowView`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/system/banned-ips/{id}/` | Bannedipdetail | `BannedIPDetailView`<br>model `BannedIP`<br>ser `BannedIPSerializer`<br><small>fields: `id, banned_by_name, ip_address, reason, banned_at, expires_at, banned_by`</small> |
| GET, PUT, PATCH, DELETE | `/api/system/connected-apps/{id}/` | Connectedappdetail | `ConnectedAppDetailView`<br>model `ConnectedApp`<br>ser `ConnectedAppSerializer`<br><small>fields: `id, client_secret, name, app_type, client_id, is_active, created_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/system/cron-jobs/{id}/` | Cronjobdetail | `CronJobDetailView`<br>model `CronJob`<br>ser `CronJobSerializer`<br><small>fields: `id, name, command, schedule, is_active, last_run_at, last_status, created_at`</small> |
| POST | `/api/system/cron-jobs/{id}/toggle-active/` | Cronjobtoggleactive | `CronJobToggleActiveView`<br>(no serializer_class) |

## Calendar Events

`5` endpoints under **`/api/calendar/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/calendar/events/` | Calendareventlistcreate | `CalendarEventListCreateView`<br>model `CalendarEvent`<br>(no serializer_class) |
| GET, POST | `/api/calendar/holidays/` | Holidaylistcreate | `HolidayListCreateView`<br>model `Holiday`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/calendar/events/{id}/` | Calendareventdetail | `CalendarEventDetailView`<br>model `CalendarEvent`<br>ser `CalendarEventSerializer`<br><small>fields: `id, title, description, event_type, start_datetime, end_datetime, is_all_day, location, color, created_by, created_by_name, created_by_email, attendees, attendee_ids, attendee_names, is_active, created_at, updated_at`</small> |
| GET, PUT, PATCH, DELETE | `/api/calendar/holidays/{id}/` | Holidaydetail | `HolidayDetailView`<br>model `Holiday`<br>ser `HolidaySerializer`<br><small>fields: `id, name, date, description, type, holiday_status, is_recurring_yearly, is_active, created_at`</small> |
| GET | `/api/calendar/holidays/upcoming/` | Upcomingholidays | `UpcomingHolidaysView`<br>(no serializer_class) |

## Invitations

`4` endpoints under **`/api/invitations/`**

| Method | Endpoint | Purpose | View / Model / Serializer |
|--------|----------|---------|----------------------------|
| GET, POST | `/api/invitations/` | Invitationlistcreate | `InvitationListCreateView`<br>model `Invitation`<br>(no serializer_class) |
| GET, PUT, PATCH, DELETE | `/api/invitations/{id}/` | Invitationdetail | `InvitationDetailView`<br>model `Invitation`<br>ser `InvitationSerializer`<br><small>fields: `id, invited_by_name, email, role, token, status, sent_at, accepted_at, expires_at, created_at, invited_by`</small> |
| POST | `/api/invitations/{id}/resend/` | Invitationresend | `InvitationResendView`<br>(no serializer_class) |
| POST | `/api/invitations/accept/{token}/` | Invitationaccept | `InvitationAcceptView`<br>(no serializer_class) |
