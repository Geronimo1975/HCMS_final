from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.translation import gettext as _
from django.urls import reverse
from django.utils.html import strip_tags

from .models import Booking, BookingNotification


@receiver(post_save, sender=Booking)
def handle_booking_status_change(sender, instance, created, **kwargs):
    """
    Signal handler for booking status changes.
    Sends email notifications and creates notification records.
    """
    if created:
        # New booking created
        send_booking_notification(instance, 'created')
    else:
        # Booking status changed
        send_booking_notification(instance, 'status_changed')


def send_booking_notification(booking, notification_type):
    """
    Send email notification for booking status changes.
    """
    # Prepare email context
    context = {
        'booking': booking,
        'booking_url': (
            settings.SITE_URL + 
            reverse('bookings:detail', args=[booking.pk])
        ),
        'support_email': settings.SUPPORT_EMAIL,
    }

    # Render email template
    html_message = render_to_string(
        'bookings/email/booking_status.html',
        context
    )

    # Send email to customer
    send_mail(
        subject=_('Booking Status Update - {}').format(
            booking.get_status_display()
        ),
        message=strip_tags(html_message),  # Plain text version
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.customer.email],
        html_message=html_message,
        fail_silently=False,
    )

    # Create notification record
    BookingNotification.objects.create(
        recipient=booking.customer,
        notification_type=notification_type,
        message=_('Your booking status has been updated to: {}').format(
            booking.get_status_display()
        )
    )

    # If booking is confirmed, send notification to provider
    if booking.status == 'confirmed':
        send_mail(
            subject=_('New Booking Confirmation'),
            message=strip_tags(html_message),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.provider.email],
            html_message=html_message,
            fail_silently=False,
        )

        BookingNotification.objects.create(
            recipient=booking.provider,
            notification_type='provider_notification',
            message=_('You have a new confirmed booking for {}').format(
                booking.start_time.strftime('%Y-%m-%d %H:%M')
            )
        ) 