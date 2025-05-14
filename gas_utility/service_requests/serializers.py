from rest_framework import serializers
from .models import (
    ServiceRequestCategory, ServiceRequest, 
    ServiceAttachment, Comment
)
from accounts.serializers import UserSerializer


class ServiceRequestCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequestCategory
        fields = ['id', 'name', 'description', 'is_active']


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'service_request', 'author', 'author_name', 'text', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']
    
    def get_author_name(self, obj):
        return obj.author.full_name
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ServiceAttachmentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceAttachment
        fields = ['id', 'service_request', 'file', 'file_name', 'file_type', 'uploaded_by', 'uploaded_by_name', 'uploaded_at']
        read_only_fields = ['file_name', 'file_type', 'uploaded_by', 'uploaded_at']
    
    def get_uploaded_by_name(self, obj):
        if obj.uploaded_by:
            return obj.uploaded_by.full_name
        return None
    
    def create(self, validated_data):
        # Set uploaded_by to current user
        validated_data['uploaded_by'] = self.context['request'].user
        
        # Extract file name and type
        file = validated_data.get('file')
        if file:
            validated_data['file_name'] = file.name
            validated_data['file_type'] = file.content_type
        
        return super().create(validated_data)


class ServiceRequestListSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    technician_name = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    priority_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'title', 'category', 'category_name', 'customer', 'customer_name',
            'technician', 'technician_name', 'status', 'status_display', 'priority',
            'priority_display', 'scheduled_date', 'created_at', 'updated_at'
        ]
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None
    
    def get_customer_name(self, obj):
        return obj.customer.full_name
    
    def get_technician_name(self, obj):
        return obj.technician.full_name if obj.technician else None
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_priority_display(self, obj):
        return obj.get_priority_display()


class ServiceRequestDetailSerializer(serializers.ModelSerializer):
    category = ServiceRequestCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceRequestCategory.objects.filter(is_active=True),
        source='category',
        write_only=True
    )
    customer = UserSerializer(read_only=True)
    technician = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    attachments = ServiceAttachmentSerializer(many=True, read_only=True)
    status_display = serializers.SerializerMethodField()
    priority_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'title', 'description', 'category', 'category_id', 'customer',
            'technician', 'status', 'status_display', 'priority', 'priority_display',
            'service_address', 'scheduled_date', 'scheduled_time_slot',
            'created_at', 'updated_at', 'resolution_notes', 'comments', 'attachments'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_status_display(self, obj):
        return obj.get_status_display()
    
    def get_priority_display(self, obj):
        return obj.get_priority_display()
    
    def create(self, validated_data):
        # Set customer to current user
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)


class ServiceRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = [
            'title', 'description', 'category', 'priority',
            'service_address', 'scheduled_date', 'scheduled_time_slot'
        ]
    
    def create(self, validated_data):
        # Set customer to current user
        validated_data['customer'] = self.context['request'].user
        # Set initial status
        validated_data['status'] = ServiceRequest.STATUS_NEW
        return super().create(validated_data)


class ServiceRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = [
            'title', 'description', 'category', 'technician', 'status', 
            'priority', 'service_address', 'scheduled_date', 
            'scheduled_time_slot', 'resolution_notes'
        ]
        read_only_fields = ['customer']