from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import CustomerProfile, TechnicianProfile

User = get_user_model()


class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['service_address', 'billing_address', 'meter_number']


class TechnicianProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicianProfile
        fields = ['employee_id', 'specialization', 'certification']


class UserSerializer(serializers.ModelSerializer):
    customer_profile = CustomerProfileSerializer(required=False)
    technician_profile = TechnicianProfileSerializer(required=False, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'phone_number', 
            'address', 'account_number', 'is_customer', 'is_technician',
            'customer_profile', 'technician_profile'
        ]
        read_only_fields = ['id', 'is_active', 'is_staff', 'is_superuser']
    
    def update(self, instance, validated_data):
        customer_profile_data = validated_data.pop('customer_profile', None)
        
        # Update User fields
        user = super().update(instance, validated_data)
        
        # Update or create CustomerProfile if needed
        if customer_profile_data and user.is_customer:
            customer_profile, created = CustomerProfile.objects.get_or_create(user=user)
            for key, value in customer_profile_data.items():
                setattr(customer_profile, key, value)
            customer_profile.save()
        
        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    customer_profile = CustomerProfileSerializer(required=False)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'first_name', 'last_name', 
            'phone_number', 'address', 'account_number', 'is_customer', 
            'is_technician', 'customer_profile'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        customer_profile_data = validated_data.pop('customer_profile', None)
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            address=validated_data.get('address', ''),
            account_number=validated_data.get('account_number', None),
            is_customer=validated_data.get('is_customer', True),
            is_technician=validated_data.get('is_technician', False),
        )
        
        # Create customer profile if needed
        if customer_profile_data and user.is_customer:
            CustomerProfile.objects.create(user=user, **customer_profile_data)
        
        return user


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "New password fields didn't match."})
        return attrs