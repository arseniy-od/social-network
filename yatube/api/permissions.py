from rest_framework import permissions
from loguru import logger

logger.add('debug.json', format="{time} {level} {message}",
           level="DEBUG", rotation="1 week", compression="zip",
           serialize=True)


class IsAdminOrSelf(permissions.IsAdminUser):
    """
    Allow access to admin users or the user himself.
    """
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        elif (request.user and type(obj) == type(request.user) and
              obj == request.user):
            return True
        return False


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
