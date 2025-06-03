from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.businesses.models import Business, BusinessHours


class ServiceCategory(models.Model):
    """
    Model for categorizing salon services.
    """
    name = models.CharField(_('category name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    icon = models.CharField(_('icon class'), max_length=50, blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('service category')
        verbose_name_plural = _('service categories')
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    """
    Model representing a service offered by a business.
    """
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='services'
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='services'
    )
    name = models.CharField(_('service name'), max_length=200)
    description = models.TextField(_('description'))
    duration = models.DurationField(_('duration'))
    price = models.DecimalField(
        _('price'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(
        _('currency'),
        max_length=3,
        default='EUR'
    )
    image = models.ImageField(
        _('service image'),
        upload_to='service_images/',
        null=True,
        blank=True
    )
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('service')
        verbose_name_plural = _('services')
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.business.name} - {self.name}"


class ServiceProvider(models.Model):
    """
    Model for linking services with staff members who can provide them.
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='providers'
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='provided_services'
    )
    is_primary = models.BooleanField(_('primary provider'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('service provider')
        verbose_name_plural = _('service providers')
        unique_together = ['service', 'provider']
        ordering = ['-is_primary', 'provider__username']

    def __str__(self):
        return f"{self.provider.get_full_name()} - {self.service.name}"


class ServiceAvailability(models.Model):
    """
    Model for managing service availability and scheduling.
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='availability'
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='service_availability'
    )
    day_of_week = models.CharField(
        max_length=9,
        choices=BusinessHours.DayOfWeek.choices
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('service availability')
        verbose_name_plural = _('service availability')
        unique_together = ['service', 'provider', 'day_of_week']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return (
            f"{self.service.name} - {self.provider.get_full_name()} - "
            f"{self.get_day_of_week_display()}"
        ) 