from django.shortcuts import get_object_or_404
from rest_framework import generics,permissions, status, viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from gas_utility import settings
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    ServiceRequestCategory, ServiceRequest, 
    ServiceAttachment, Comment
)
from .serializers import (
    ServiceRequestCategorySerializer, ServiceRequestListSerializer,
    ServiceRequestDetailSerializer, ServiceRequestCreateSerializer,
    ServiceRequestUpdateSerializer, CommentSerializer,
    ServiceAttachmentSerializer
)
from .permissions import (
    IsCustomerOrTechnician, IsOwnerOrTechnician, 
    IsCustomer, IsTechnician
)


class ServiceRequestCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for service request categories"""
    queryset = ServiceRequestCategory.objects.filter(is_active=True)
    serializer_class = ServiceRequestCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ServiceRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for service requests"""
    queryset = ServiceRequest.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category', 'scheduled_date']
    search_fields = ['title', 'description', 'service_address']
    ordering_fields = ['created_at', 'updated_at', 'scheduled_date', 'priority']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """Set custom permissions for different actions"""
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated, IsCustomer]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrTechnician]
        elif self.action in ['destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated, IsCustomerOrTechnician]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Select serializer based on action"""
        if self.action == 'list':
            return ServiceRequestListSerializer
        elif self.action == 'create':
            return ServiceRequestCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ServiceRequestUpdateSerializer
        return ServiceRequestDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role"""
        user = self.request.user
        
        if user.is_staff:
            # Admin users can see all requests
            return ServiceRequest.objects.all()
        elif user.is_technician:
            # Technicians can see requests assigned to them or unassigned
            return ServiceRequest.objects.filter(technician=user) | ServiceRequest.objects.filter(technician__isnull=True)
        else:
            # Regular customers can only see their own requests
            return ServiceRequest.objects.filter(customer=user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsTechnician])
    def assign_to_me(self, request, pk=None):
        """Action to allow technicians to assign a service request to themselves"""
        service_request = self.get_object()
        
        if service_request.technician:
            return Response(
                {"detail": "This service request is already assigned to a technician."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service_request.technician = request.user
        service_request.status = ServiceRequest.STATUS_ASSIGNED
        service_request.save()
        
        serializer = self.get_serializer(service_request)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for comments"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrTechnician]
    
    def get_queryset(self):
        service_request_id = self.kwargs.get('service_request_pk')
        return Comment.objects.filter(service_request_id=service_request_id)
    
    def perform_create(self, serializer):
        service_request_id = self.kwargs.get('service_request_pk')
        service_request = get_object_or_404(ServiceRequest, id=service_request_id)
        serializer.save(author=self.request.user, service_request=service_request)


class ServiceAttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for service attachments"""
    queryset = ServiceAttachment.objects.all()
    serializer_class = ServiceAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCustomerOrTechnician]
    
    def get_queryset(self):
        service_request_id = self.kwargs.get('service_request_pk')
        return ServiceAttachment.objects.filter(service_request_id=service_request_id)
    
    def perform_create(self, serializer):
        service_request_id = self.kwargs.get('service_request_pk')
        service_request = get_object_or_404(ServiceRequest, id=service_request_id)
        
        # Check file size before saving
        if self.request.FILES.get('file').size > settings.MAX_UPLOAD_SIZE:
            return Response({"error": "File too large"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save(uploaded_by=self.request.user, service_request=service_request)
    
    def get_permissions(self):
        if self.action in ['destroy']:
            return [permissions.IsAuthenticated(), IsOwnerOrTechnician()]
        return super().get_permissions()