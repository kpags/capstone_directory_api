from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsActive(BasePermission):
    def has_permission(self, request, view):
        user = request.instance
        method = request.method
        print("Method:", method)
        print("User:", request.instance)
        return bool(user.is_active)
    
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.instance
        return user.role.lower() in ["admin", "administrator"]