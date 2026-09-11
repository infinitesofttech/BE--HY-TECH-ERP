from rest_framework.permissions import BasePermission


class IsHROrAdmin(BasePermission):
    message = 'HR or Admin access required.'

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated
            and (user.is_superuser or user.role in ('admin', 'hr'))
        )


class IsStaffOrAdmin(BasePermission):
    message = 'Staff or Admin access required.'

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated
            and (user.is_superuser or user.role in ('admin', 'hr', 'staff'))
        )