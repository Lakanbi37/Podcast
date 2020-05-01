from memberships.models import UserMembership
from rest_framework.permissions import BasePermission


class IsSufficientMembership(BasePermission):
    MY_SAFE_METHODS = ["GET"]

    def has_permission(self, request, view):
        return bool(request.method in self.MY_SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        try:
            user_membership = UserMembership.objects.get(user=request.user)
        except Exception as e:
            return False
        return bool(request.method in self.MY_SAFE_METHODS
                    or user_membership.membership == obj.category.membership)


class IsCategoryMembership(BasePermission):
    MY_SAFE_METHODS = ["GET"]

    def has_permission(self, request, view):
        return bool(request.method in self.MY_SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        try:
            user_membership = UserMembership.objects.get(user=request.user)
        except Exception as e:
            return False
        return bool(
            user_membership.membership == obj.membership
            or request.method in self.MY_SAFE_METHODS)
