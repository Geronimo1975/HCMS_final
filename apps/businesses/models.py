from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Business(models.Model):
    """
    Model representing a salon or wellness business.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_businesses'
    )
    name = models.CharField(_('business name'), max_length=200)
    description = models.TextField(_('description'))
    address = models.CharField(_('address'), max_length=200)
    city = models.CharField(_('city'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=10)
    country = models.CharField(_('country'), max_length=100, default='Germany')
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    phone = models.CharField(_('phone number'), max_length=20)
    email = models.EmailField(_('email address'))
    website = models.URLField(_('website'), blank=True)
    logo = models.ImageField(
        _('logo'),
        upload_to='business_logos/',
        null=True,
        blank=True
    )
    cover_image = models.ImageField(
        _('cover image'),
        upload_to='business_covers/',
        null=True,
        blank=True
    )
    rating = models.DecimalField(
        _('rating'),
        max_digits=3,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)]
    )
    is_verified = models.BooleanField(_('verified'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('business')
        verbose_name_plural = _('businesses')
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class BusinessHours(models.Model):
    """
    Model for storing business operating hours.
    """
    class DayOfWeek(models.TextChoices):
        MONDAY = 'monday', _('Monday')
        TUESDAY = 'tuesday', _('Tuesday')
        WEDNESDAY = 'wednesday', _('Wednesday')
        THURSDAY = 'thursday', _('Thursday')
        FRIDAY = 'friday', _('Friday')
        SATURDAY = 'saturday', _('Saturday')
        SUNDAY = 'sunday', _('Sunday')

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='operating_hours'
    )
    day_of_week = models.CharField(
        max_length=10,
        choices=DayOfWeek.choices
    )
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_closed = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('business hours')
        verbose_name_plural = _('business hours')
        unique_together = ['business', 'day_of_week']
        ordering = ['day_of_week']

    def __str__(self):
        if self.is_closed:
            return f"{self.business.name} - {self.get_day_of_week_display()} (Closed)"
        return f"{self.business.name} - {self.get_day_of_week_display()} ({self.opening_time} - {self.closing_time})"


class BusinessImage(models.Model):
    """
    Model for storing business images.
    """
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='business_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('business image')
        verbose_name_plural = _('business images')
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"{self.business.name} - {self.caption or 'Image'}"


class BusinessReview(models.Model):
    """
    Model for storing customer reviews of businesses.
    """
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='business_reviews'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('business review')
        verbose_name_plural = _('business reviews')
        ordering = ['-created_at']
        unique_together = ['business', 'customer']

    def __str__(self):
        return f"Review by {self.customer.email} for {self.business.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update business average rating
        self.business.rating = self.business.reviews.aggregate(
            models.Avg('rating')
        )['rating__avg'] or 0
        self.business.save() 