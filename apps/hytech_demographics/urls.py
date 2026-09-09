from django.urls import path
from .views import VillageViewSet

urlpatterns = [
    path('family-tree/<str:family_id>/', VillageViewSet.as_view({
        'get': 'family_tree',
    }), name='village-family-tree'),
    path('<str:code>/family-tree/<str:family_id>/', VillageViewSet.as_view({
        'get': 'family_tree_by_village',
    }), name='village-code-family-tree'),
    path('', VillageViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='village-list'),
    path('<str:code>/', VillageViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='village-detail'),
]
