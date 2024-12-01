from rest_framework.permissions import BasePermission, SAFE_METHODS
from utils.auth import JWTAuthentication


class IsActive(BasePermission):
    def has_permission(self, request, view):
        method = request.method

        if method == "GET":
            if not hasattr(request, "instance"):
                return False
            
            user = request.instance
            return bool(user.is_active)
        else:
            auth = JWTAuthentication()
            payload = auth.authenticate(request=request)

            if payload is None:
                return False
            
            user = payload.get("instance", None)
            return bool(user.is_active)
        
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        method = request.method

        if method == "GET":
            if not hasattr(request, "instance"):
                return False
            
            return bool(request.instance and request.instance.is_active)
        else:
            auth = JWTAuthentication()
            payload = auth.authenticate(request=request)
            
            if payload is None:
                return False
            
            user = payload.get("instance", None)
            return bool(user.role.lower() in ["admin", "administrator"])

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        method = request.method

        if method == "GET":
            user = request.instance
            
            if not hasattr(request, "instance"):
                return False
            
            return bool(
                user.is_active and user.role.lower() in ["admin", "administrator"]
            )
        else:
            auth = JWTAuthentication()
            payload = auth.authenticate(request=request)
            
            if payload is None:
                return False

            user = payload.get("instance", None)
            return bool(
                user.is_active and user.role.lower() in ["admin", "administrator"]
            )


class IsCoordinator(BasePermission):

    def has_permission(self, request, view):
        method = request.method

        if method == "GET":
            user = request.instance
            
            if not hasattr(request, "instance"):
                return False
            
            return bool(
                user.is_active
                and user.role.lower() in ["coordinator", "capstone coordinator"]
            )
        else:
            auth = JWTAuthentication()
            payload = auth.authenticate(request=request)
            
            if payload is None:
                return False

            user = payload.get("instance", None)
            return bool(
                user.is_active
                and user.role.lower() in ["coordinator", "capstone coordinator"]
            )

class IsAdminOrCoordinator(BasePermission):
    def has_permission(self, request, view):
        method = request.method

        if method == "GET":
            user = request.instance
            
            if not hasattr(request, "instance"):
                return False
            
            return bool(
                user.is_active
                and user.role.lower() in ["coordinator", "capstone coordinator", "admin", "administrator"]
            )
        else:
            auth = JWTAuthentication()
            payload = auth.authenticate(request=request)
            
            if payload is None:
                return False
            
            user = payload.get("instance", None)
            return bool(
                user.is_active
                and user.role.lower() in["coordinator", "capstone coordinator", "admin", "administrator"]
            )

class IsFaculty(BasePermission):

    def has_permission(self, request, view):
        method = request.method

        if method == "GET":
            user = request.instance
            
            if not hasattr(request, "instance"):
                return False
            
            return bool(user.is_active and user.role.lower() in ["faculty"])
        else:
            auth = JWTAuthentication()
            payload = auth.authenticate(request=request)
            
            if payload is None:
                return False
            
            user = payload.get("instance", None)
            return bool(user.is_active and user.role.lower() in ["faculty"])
