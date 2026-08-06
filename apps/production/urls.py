from django.urls import path
from . import views

urlpatterns = [
    path('machines/', views.MachineListCreateView.as_view(), name='machine-list-create'),
    path('machines/<int:pk>/', views.MachineDetailView.as_view(), name='machine-detail'),

    path('boms/', views.BomListCreateView.as_view(), name='bom-list-create'),
    path('boms/<int:pk>/', views.BomDetailView.as_view(), name='bom-detail'),

    path('job-orders/', views.JobOrderListCreateView.as_view(), name='job-order-list-create'),
    path('job-orders/<int:pk>/', views.JobOrderDetailView.as_view(), name='job-order-detail'),
    path('job-orders/<int:pk>/check-stock/', views.JobOrderCheckStockView.as_view(), name='job-order-check-stock'),
    path('job-orders/<int:pk>/issue-material/', views.JobOrderIssueMaterialView.as_view(), name='job-order-issue-material'),
    path('job-orders/<int:pk>/create-requisition/', views.JobOrderCreateRequisitionView.as_view(), name='job-order-create-requisition'),
    path('job-orders/<int:pk>/start/', views.JobOrderStartProductionView.as_view(), name='job-order-start'),
    path('job-orders/<int:pk>/rework/', views.JobOrderReworkView.as_view(), name='job-order-rework'),
    path('job-orders/<int:pk>/qc/', views.JobOrderQcView.as_view(), name='job-order-qc'),
    path('job-orders/<int:pk>/dispatch/', views.JobOrderDispatchView.as_view(), name='job-order-dispatch'),

    path('material-issues/', views.MaterialIssueSlipListView.as_view(), name='material-issue-list'),
    path('material-issues/<int:pk>/', views.MaterialIssueSlipDetailView.as_view(), name='material-issue-detail'),

    path('requisitions/', views.PurchaseRequisitionListCreateView.as_view(), name='requisition-list-create'),
    path('requisitions/<int:pk>/', views.PurchaseRequisitionDetailView.as_view(), name='requisition-detail'),
    path('requisitions/<int:pk>/approve/', views.PurchaseRequisitionApproveView.as_view(), name='requisition-approve'),
    path('requisitions/<int:pk>/reject/', views.PurchaseRequisitionRejectView.as_view(), name='requisition-reject'),

    path('grns/', views.GoodsReceiptNoteListCreateView.as_view(), name='grn-list-create'),
    path('grns/<int:pk>/', views.GoodsReceiptNoteDetailView.as_view(), name='grn-detail'),
    path('grns/<int:pk>/receive/', views.GoodsReceiptNoteReceiveView.as_view(), name='grn-receive'),
    path('grns/<int:pk>/inspect/', views.GoodsReceiptNoteInspectView.as_view(), name='grn-inspect'),

    path('inspections/', views.QualityInspectionListCreateView.as_view(), name='inspection-list-create'),
    path('inspections/<int:pk>/', views.QualityInspectionDetailView.as_view(), name='inspection-detail'),
    path('inspections/<int:pk>/result/', views.QualityInspectionResultView.as_view(), name='inspection-result'),

    path('processes/', views.ProductionProcessListView.as_view(), name='process-list'),
    path('processes/<int:pk>/advance/', views.ProductionProcessAdvanceView.as_view(), name='process-advance'),

    path('finished-goods/', views.FinishedGoodsListView.as_view(), name='finished-goods-list'),
    path('finished-goods/<int:pk>/', views.FinishedGoodsDetailView.as_view(), name='finished-goods-detail'),

    path('dispatches/', views.DispatchListCreateView.as_view(), name='dispatch-list-create'),
    path('dispatches/<int:pk>/', views.DispatchDetailView.as_view(), name='dispatch-detail'),
    path('dispatches/<int:pk>/mark-dispatched/', views.DispatchMarkDispatchedView.as_view(), name='dispatch-mark-dispatched'),
]
