from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.businesses.models import Business


class SubscriptionPlan(models.Model):
    """
    Model for managing subscription plans.
    """
    class PlanType(models.TextChoices):
        FREEMIUM = 'freemium', _('Freemium')
        PREMIUM = 'premium', _('Premium')

    name = models.CharField(_('plan name'), max_length=100)
    plan_type = models.CharField(
        max_length=20,
        choices=PlanType.choices
    )
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(
        max_length=3,
        default='EUR'
    )
    interval = models.CharField(
        max_length=20,
        choices=[
            ('monthly', _('Monthly')),
            ('yearly', _('Yearly')),
        ],
        default='monthly'
    )
    stripe_price_id = models.CharField(max_length=100)
    max_bookings = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('Maximum number of bookings per month (null for unlimited)')
    )
    features = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('subscription plan')
        verbose_name_plural = _('subscription plans')
        ordering = ['price']

    def __str__(self):
        return f"{self.name} ({self.get_interval_display()})"


class Subscription(models.Model):
    """
    Model for tracking business subscriptions.
    """
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        PAST_DUE = 'past_due', _('Past Due')
        CANCELED = 'canceled', _('Canceled')
        UNPAID = 'unpaid', _('Unpaid')
        TRIALING = 'trialing', _('Trialing')

    business = models.OneToOneField(
        Business,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name='subscriptions'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TRIALING
    )
    stripe_subscription_id = models.CharField(max_length=100, unique=True)
    stripe_customer_id = models.CharField(max_length=100)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.business.name} - {self.plan.name}"


class Payment(models.Model):
    """
    Model for tracking subscription payments.
    """
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        SUCCEEDED = 'succeeded', _('Succeeded')
        FAILED = 'failed', _('Failed')
        REFUNDED = 'refunded', _('Refunded')

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(
        max_length=3,
        default='EUR'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    stripe_payment_intent_id = models.CharField(max_length=100, unique=True)
    stripe_invoice_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.stripe_payment_intent_id} - {self.amount} {self.currency}"


class PaymentMethod(models.Model):
    """
    Model for storing customer payment methods.
    """
    class Type(models.TextChoices):
        CARD = 'card', _('Card')
        SEPA = 'sepa', _('SEPA Direct Debit')
        PAYPAL = 'paypal', _('PayPal')

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    type = models.CharField(
        max_length=20,
        choices=Type.choices
    )
    stripe_payment_method_id = models.CharField(max_length=100, unique=True)
    is_default = models.BooleanField(default=False)
    last_four = models.CharField(max_length=4, blank=True)
    expiry_month = models.IntegerField(null=True, blank=True)
    expiry_year = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('payment method')
        verbose_name_plural = _('payment methods')
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.get_type_display()} - {self.last_four} for {self.business.name}" 