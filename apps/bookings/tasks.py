from celery import shared_task
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from datetime import timedelta

from .models import Booking, BookingNotification, BookingStatus


@shared_task
def send_booking_reminders():
    """
    Send reminders for upcoming bookings.
    """
    # Get bookings happening in the next 24 hours
    tomorrow = timezone.now() + timedelta(days=1)
    upcoming_bookings = Booking.objects.filter(
        start_time__gte=timezone.now(),
        start_time__lte=tomorrow,
        status=BookingStatus.CONFIRMED,
        is_paid=True
    ).select_related('customer', 'provider', 'service', 'business')

    for booking in upcoming_bookings:
        # Send reminder to customer
        context = {
            'booking': booking,
            'booking_url': (
                settings.SITE_URL + 
                f'/bookings/{booking.id}/'
            ),
            'support_email': settings.SUPPORT_EMAIL,
        }

        # Render email template
        html_message = render_to_string(
            'bookings/email/booking_reminder.html',
            context
        )

        # Send email
        send_mail(
            subject=_('Reminder: Your booking tomorrow'),
            message=strip_tags(html_message),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.customer.email],
            html_message=html_message,
            fail_silently=False,
        )

        # Create notification record
        BookingNotification.objects.create(
            recipient=booking.customer,
            booking=booking,
            notification_type='reminder',
            message=_('Reminder: You have a booking tomorrow at {}').format(
                booking.start_time.strftime('%H:%M')
            )
        )

        # Send reminder to provider
        send_mail(
            subject=_('Reminder: You have a booking tomorrow'),
            message=strip_tags(html_message),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.provider.email],
            html_message=html_message,
            fail_silently=False,
        )

        BookingNotification.objects.create(
            recipient=booking.provider,
            booking=booking,
            notification_type='provider_reminder',
            message=_('Reminder: You have a booking tomorrow at {}').format(
                booking.start_time.strftime('%H:%M')
            )
        )

    return f"Sent reminders for {upcoming_bookings.count()} bookings" 