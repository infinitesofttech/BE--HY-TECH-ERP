from django.urls import path
from . import views

urlpatterns = [
    path('types/', views.LeaveTypeListCreateView.as_view(), name='leave-type-list'),
    path('types/<int:pk>/', views.LeaveTypeDetailView.as_view(), name='leave-type-detail'),
    path('request/', views.LeaveCreateView.as_view(), name='leave-create'),
    path('admin-assign/', views.LeaveAdminAssignView.as_view(), name='leave-admin-assign'),
    path('', views.LeaveListView.as_view(), name='leave-list'),
    path('my/', views.MyLeaveListView.as_view(), name='leave-my'),
    path('pending-approvals/', views.PendingApprovalsView.as_view(), name='leave-pending-approvals'),
    path('<int:pk>/', views.LeaveDetailView.as_view(), name='leave-detail'),
    path('<int:pk>/approve/', views.LeaveApproveView.as_view(), name='leave-approve'),
    path('<int:pk>/reject/', views.LeaveRejectView.as_view(), name='leave-reject'),
    path('balance/<int:employee_id>/', views.LeaveBalanceView.as_view(), name='leave-balance'),
    path('workflow/', views.LeaveApprovalWorkflowListCreateView.as_view(), name='approval-workflow-list'),
    path('workflow/<int:pk>/', views.LeaveApprovalWorkflowDetailView.as_view(), name='approval-workflow-detail'),
    path('allocations/', views.LeaveAllocationListCreateView.as_view(), name='leave-allocation-list'),
    path('allocations/<int:pk>/', views.LeaveAllocationDetailView.as_view(), name='leave-allocation-detail'),
]
