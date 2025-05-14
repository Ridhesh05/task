from django.contrib import admin
from .models import User, CustomerProfile, TechnicianProfile


class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    verbose_name_plural = 'Customer Profile'


class TechnicianProfileInline(admin.StackedInline):
    model = TechnicianProfile
    can_delete = False
    verbose_name_plural = 'Technician Profile'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_customer', 'is_technician', 'is_staff')
    list_filter = ('is_customer', 'is_technician', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'account_number')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'address', 'account_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_customer', 'is_technician')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'is_customer', 'is_technician'),
        }),
    )
    
    def get_inlines(self, request, obj=None):
        if obj:
            inlines = []
            if obj.is_customer:
                inlines.append(CustomerProfileInline)
            if obj.is_technician:
                inlines.append(TechnicianProfileInline)
            return inlines
        return []


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'meter_number')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'meter_number')


@admin.register(TechnicianProfile)
class TechnicianProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'specialization')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'employee_id')