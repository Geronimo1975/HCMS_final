from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom user model with additional fields for salon management system.
    """
    class UserType(models.TextChoices):
        CUSTOMER = 'customer', _('Customer')
        PROVIDER = 'provider', _('Provider')
        ADMIN = 'admin', _('Admin')

    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.CUSTOMER
    )
    phone_number = models.CharField(max_length=20, blank=True)
    preferred_language = models.CharField(
        max_length=2,
        choices=[
            ('de', _('German')),
            ('en', _('English')),
            ('es', _('Spanish')),
        ],
        default='de'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    @property
    def is_provider(self):
        return self.user_type == self.UserType.PROVIDER

    @property
    def is_customer(self):
        return self.user_type == self.UserType.CUSTOMER

    @property
    def is_admin(self):
        return self.user_type == self.UserType.ADMIN 