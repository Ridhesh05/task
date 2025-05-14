from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import (
    ServiceRequestCategoryViewSet, ServiceRequestViewSet,
    CommentViewSet, ServiceAttachmentViewSet
)

app_name = 'service_requests'

# Root router
router = DefaultRouter()
router.register(r'categories', ServiceRequestCategoryViewSet)
router.register(r'requests', ServiceRequestViewSet)

# Nested routers for comments and attachments
service_request_router = routers.NestedSimpleRouter(router, r'requests', lookup='service_request')
service_request_router.register(r'comments', CommentViewSet, basename='service-request-comments')
service_request_router.register(r'attachments', ServiceAttachmentViewSet, basename='service-request-attachments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(service_request_router.urls)),
]