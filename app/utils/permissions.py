from rest_framework.permissions import BasePermission, SAFE_METHODS
from utils.auth import JWTAuthentication


class IsActive(BasePermission):
    def has_permission(self, request, view):
        method = request.method

        if method == "GET":
            user = request.instance
            return bool(user.is_active)
        else:
            auth = JWTAuthentication()
            payload = auth.authenticate(request=request)

            user = payload.get("instance", None)
            return bool(user.is_active)


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        method = request.method

        if method == "GET":
            user = request.instance
            return bool(
                user.is_active and user.role.lower() in ["admin", "administrator"]
            )
        else:
            auth = JWTAuthentication()
            payload = auth.authenticate(request=request)

            user = payload.get("instance", None)
            return bool(
                user.is_active and user.role.lower() in ["admin", "administrator"]
            )


class IsCoordinator(BasePermission):

    def has_permission(self, request, view):
        method = request.method

        if method == "GET":
            user = request.instance
            return bool(
                user.is_active
                and user.role.lower() in ["coordinator", "capstone coordinator"]
            )
        else:
            auth = JWTAuthentication()
            payload = auth.authenticate(request=request)

            user = payload.get("instance", None)
            return bool(
                user.is_active
                and user.role.lower() in ["coordinator", "capstone coordinator"]
            )


class IsFaculty(BasePermission):

    def has_permission(self, request, view):
        method = request.method

        if method == "GET":
            user = request.instance
            return bool(user.is_active and user.role.lower() in ["faculty"])
        else:
            auth = JWTAuthentication()
            payload = auth.authenticate(request=request)

            user = payload.get("instance", None)
            return bool(user.is_active and user.role.lower() in ["faculty"])