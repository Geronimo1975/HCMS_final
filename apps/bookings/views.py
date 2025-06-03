from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator

from .models import Booking, BookingStatus
from apps.services.models import Service, ServiceAvailability


class BookingListView(LoginRequiredMixin, ListView):
    """
    View for displaying user's bookings.
    """
    model = Booking
    template_name = 'bookings/list.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get_queryset(self):
        # Return all bookings for pagination compatibility
        return Booking.objects.filter(customer=self.request.user).select_related('service', 'provider', 'business')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context['upcoming_bookings'] = Booking.objects.filter(
            customer=self.request.user,
            start_time__gte=now,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED]
        ).select_related('service', 'provider', 'business')
        context['past_bookings'] = Booking.objects.filter(
            Q(start_time__lt=now) |
            Q(status__in=[
                BookingStatus.COMPLETED,
                BookingStatus.CANCELLED,
                BookingStatus.NO_SHOW
            ]),
            customer=self.request.user
        ).select_related('service', 'provider', 'business')
        return context


class BookingDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying booking details.
    """
    model = Booking
    template_name = 'bookings/detail.html'
    context_object_name = 'booking'

    def get_queryset(self):
        return Booking.objects.filter(
            customer=self.request.user
        ).select_related('service', 'provider', 'business', 'payment')


class BookingCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new booking.
    """
    model = Booking
    template_name = 'bookings/create.html'
    fields = ['service', 'provider', 'start_time', 'notes']
    success_url = reverse_lazy('bookings:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service_id = self.kwargs.get('service_id')
        if service_id:
            context['service'] = get_object_or_404(Service, id=service_id)
            context['available_slots'] = ServiceAvailability.objects.filter(
                service=context['service'],
                is_available=True,
                start_time__gt=timezone.now().time()
            )
        return context

    def form_valid(self, form):
        form.instance.customer = self.request.user
        form.instance.business = form.instance.service.business
        form.instance.price = form.instance.service.price
        form.instance.currency = form.instance.service.currency
        
        # Calculate end time based on service duration
        form.instance.end_time = (
            form.instance.start_time + 
            form.instance.service.duration
        )
        
        response = super().form_valid(form)
        messages.success(self.request, _('Booking created successfully!'))
        return response


class BookingUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing booking.
    """
    model = Booking
    template_name = 'bookings/update.html'
    fields = ['start_time', 'notes']
    success_url = reverse_lazy('bookings:list')

    def get_queryset(self):
        return Booking.objects.filter(
            customer=self.request.user,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_slots'] = ServiceAvailability.objects.filter(
            service=self.object.service,
            is_available=True,
            start_time__gt=timezone.now().time()
        )
        return context

    def form_valid(self, form):
        # Recalculate end time based on service duration
        form.instance.end_time = (
            form.instance.start_time + 
            form.instance.service.duration
        )
        
        response = super().form_valid(form)
        messages.success(self.request, _('Booking updated successfully!'))
        return response


class BookingCancelView(LoginRequiredMixin, UpdateView):
    """
    View for cancelling a booking.
    """
    model = Booking
    template_name = 'bookings/cancel.html'
    fields = []
    success_url = reverse_lazy('bookings:list')

    def get_queryset(self):
        return Booking.objects.filter(
            customer=self.request.user,
            status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED]
        )

    def form_valid(self, form):
        form.instance.status = BookingStatus.CANCELLED
        response = super().form_valid(form)
        messages.success(self.request, _('Booking cancelled successfully!'))
        return response


class BookingCalendarView(LoginRequiredMixin, TemplateView):
    """
    View for displaying the booking calendar.
    """
    template_name = 'bookings/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = self.request.user.business.providers.all()
        return context


@method_decorator(require_http_methods(["GET"]), name='dispatch')
class CalendarEventsView(LoginRequiredMixin, TemplateView):
    """
    API endpoint for getting calendar events.
    """
    def get(self, request, *args, **kwargs):
        provider_id = request.GET.get('provider_id')
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')

        bookings = Booking.objects.filter(
            Q(customer=request.user) | 
            Q(provider__business=request.user.business)
        ).select_related('service', 'provider')

        if provider_id:
            bookings = bookings.filter(provider_id=provider_id)

        if start_date and end_date:
            bookings = bookings.filter(
                start_time__gte=start_date,
                end_time__lte=end_date
            )

        events = []
        for booking in bookings:
            events.append({
                'id': booking.id,
                'title': booking.service.name,
                'start': booking.start_time.isoformat(),
                'end': booking.end_time.isoformat(),
                'providerId': booking.provider.id,
                'extendedProps': {
                    'provider': booking.provider.get_full_name(),
                    'status': booking.get_status_display(),
                    'customer': booking.customer.get_full_name()
                }
            })

        return JsonResponse({'events': events})


def get_available_slots(request):
    """
    AJAX view for getting available time slots for a service.
    """
    service_id = request.GET.get('service_id')
    date = request.GET.get('date')
    
    if not service_id or not date:
        return JsonResponse(
            {'error': _('Missing required parameters')}, 
            status=400
        )
    
    slots = ServiceAvailability.objects.filter(
        service_id=service_id,
        start_time__date=date,
        is_available=True
    ).values('id', 'start_time', 'end_time')
    
    return JsonResponse({'slots': list(slots)}) 