from django.contrib import admin
from .models import Service, ServiceCategory, ServiceProvider, ServiceAvailability
from django.utils.translation import gettext_lazy as _

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'business', 'category', 'price', 'currency', 'duration', 'is_active')
    list_filter = ('business', 'category', 'is_active', 'currency')
    search_fields = ('name', 'description', 'business__name', 'category__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'provider', 'is_primary', 'created_at')
    list_filter = ('is_primary',)
    search_fields = ('service__name', 'provider__email', 'provider__first_name', 'provider__last_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

@admin.register(ServiceAvailability)
class ServiceAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'provider', 'day_of_week', 'start_time', 'end_time', 'is_available')
    list_filter = ('day_of_week', 'is_available', 'service', 'provider')
    search_fields = ('service__name', 'provider__email')
    ordering = ('service', 'provider', 'day_of_week', 'start_time')
    readonly_fields = ('created_at', 'updated_at') 