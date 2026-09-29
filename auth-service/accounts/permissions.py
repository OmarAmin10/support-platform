from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model

User = get_user_model()
class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.role == User.Role.ADMIN

class IsAgent(BasePermission):

    def has_permission(self, request, view):
        return request.user.role == User.Role.AGENT

class IsAgentOrAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.role in [ User.Role.AGENT, User.Role.ADMIN]
    
