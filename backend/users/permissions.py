# users/permissions.py

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only admin can access"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsArchitect(BasePermission):
    """Only architect can access"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'architect'
        )


class IsClient(BasePermission):
    """Only client can access"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'client'
        )


class IsAdminOrArchitect(BasePermission):
    """Admin or Architect can access"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['admin', 'architect']
        )


class IsAdminOrClient(BasePermission):
    """Admin or Client can access"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['admin', 'client']
        )