from rest_framework import permissions


class IsCustomer(permissions.BasePermission):
    """
    Permission to allow only customers to access the resource.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_customer


class IsTechnician(permissions.BasePermission):
    """
    Permission to allow only technicians to access the resource.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_technician


class IsCustomerOrTechnician(permissions.BasePermission):
    """
    Permission to allow customers or technicians to access the resource.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_customer or request.user.is_technician or request.user.is_staff)
        )


class IsOwnerOrTechnician(permissions.BasePermission):
    """
    Permission to only allow:
    - Customers who own the service request
    - Technicians assigned to the service request
    - Staff users
    """
    def has_object_permission(self, request, view, obj):
        # Staff can do anything
        if request.user.is_staff:
            return True
            
        # Check if it's a service request
        if hasattr(obj, 'customer'):
            # Customer can only access their own requests
            if request.user.is_customer:
                return obj.customer == request.user
                
            # Technician can only access assigned requests
            if request.user.is_technician:
                return obj.technician == request.user or obj.technician is None
                
        # For attachments and comments, get the related service request
        elif hasattr(obj, 'service_request'):
            service_request = obj.service_request
            
            
            if request.user.is_customer:
                return service_request.customer == request.user
                
            if request.user.is_technician:
                return service_request.technician == request.user or service_request.technician is None
            
            
            if hasattr(obj, 'uploaded_by'):
                return obj.uploaded_by == request.user
                
        return False