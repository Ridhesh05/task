from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager to handle email as username."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model that uses email as the unique identifier instead of username."""
    
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    address = models.TextField(_('address'), blank=True)
    account_number = models.CharField(_('account number'), max_length=50, unique=True, null=True, blank=True)
    is_customer = models.BooleanField(_('customer status'), default=True)
    is_technician = models.BooleanField(_('technician status'), default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class CustomerProfile(models.Model):
    """Additional information for customers."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    service_address = models.TextField(_('service address'), blank=True)
    billing_address = models.TextField(_('billing address'), blank=True)
    meter_number = models.CharField(_('meter number'), max_length=50, blank=True)
    
    def __str__(self):
        return f"Customer Profile: {self.user.email}"


class TechnicianProfile(models.Model):
    """Additional information for technicians."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='technician_profile')
    employee_id = models.CharField(_('employee ID'), max_length=50, unique=True)
    specialization = models.CharField(_('specialization'), max_length=100, blank=True)
    certification = models.CharField(_('certification'), max_length=100, blank=True)
    
    def __str__(self):
        return f"Technician Profile: {self.user.email}"