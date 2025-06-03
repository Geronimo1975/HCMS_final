import stripe
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .models import BookingPayment, PaymentStatus

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:
    @staticmethod
    def create_payment_intent(booking):
        """
        Create a Stripe PaymentIntent for a booking.
        """
        try:
            # Create or get Stripe customer
            if not booking.customer.stripe_customer_id:
                customer = stripe.Customer.create(
                    email=booking.customer.email,
                    name=booking.customer.get_full_name(),
                    metadata={
                        'user_id': booking.customer.id
                    }
                )
                booking.customer.stripe_customer_id = customer.id
                booking.customer.save()
            else:
                customer = stripe.Customer.retrieve(
                    booking.customer.stripe_customer_id
                )

            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(booking.price * 100),  # Convert to cents
                currency=booking.currency.lower(),
                customer=customer.id,
                metadata={
                    'booking_id': booking.id,
                    'service_id': booking.service.id,
                    'business_id': booking.business.id
                },
                description=_('Payment for {}').format(booking.service.name)
            )

            # Create payment record
            payment = BookingPayment.objects.create(
                booking=booking,
                amount=booking.price,
                currency=booking.currency,
                stripe_payment_intent_id=intent.id,
                stripe_customer_id=customer.id,
                status=PaymentStatus.PENDING
            )

            return {
                'client_secret': intent.client_secret,
                'payment_id': payment.id
            }

        except stripe.error.StripeError as e:
            raise Exception(_('Payment processing error: {}').format(str(e)))

    @staticmethod
    def confirm_payment(payment_id):
        """
        Confirm a payment after successful Stripe payment.
        """
        try:
            payment = BookingPayment.objects.get(id=payment_id)
            intent = stripe.PaymentIntent.retrieve(
                payment.stripe_payment_intent_id
            )

            if intent.status == 'succeeded':
                payment.status = PaymentStatus.COMPLETED
                payment.transaction_id = intent.id
                payment.save()

                # Update booking payment status
                booking = payment.booking
                booking.is_paid = True
                booking.save()

                return True
            else:
                payment.status = PaymentStatus.FAILED
                payment.save()
                return False

        except (BookingPayment.DoesNotExist, stripe.error.StripeError) as e:
            raise Exception(_('Payment confirmation error: {}').format(str(e)))

    @staticmethod
    def refund_payment(payment_id):
        """
        Process a refund for a payment.
        """
        try:
            payment = BookingPayment.objects.get(id=payment_id)
            
            if payment.status != PaymentStatus.COMPLETED:
                raise Exception(_('Only completed payments can be refunded'))

            refund = stripe.Refund.create(
                payment_intent=payment.stripe_payment_intent_id
            )

            payment.status = PaymentStatus.REFUNDED
            payment.save()

            # Update booking payment status
            booking = payment.booking
            booking.is_paid = False
            booking.save()

            return True

        except (BookingPayment.DoesNotExist, stripe.error.StripeError) as e:
            raise Exception(_('Refund processing error: {}').format(str(e))) 