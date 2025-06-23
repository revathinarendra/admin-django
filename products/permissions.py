from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to read/edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Safe methods like GET, HEAD, OPTIONS are allowed
        if request.method in permissions.SAFE_METHODS:
            return obj.owner == request.user  # Only owner can read

        # Only the owner can modify or delete
        return obj.owner == request.user
