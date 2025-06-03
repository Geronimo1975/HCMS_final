from django.contrib import admin
from django.utils.html import format_html
from .models import Booking, BookingPayment, BookingNotification, BookingStatus
from django.utils.translation import gettext_lazy as _

# Global admin branding
admin.site.site_header = _('SalonManager Admin')
admin.site.site_title = _('SalonManager Admin Portal')
admin.site.index_title = _('Welcome to SalonManager Administration')

class BookingPaymentInline(admin.StackedInline):
    model = BookingPayment
    extra = 0
    can_delete = False
    readonly_fields = ('amount', 'currency', 'status', 'transaction_id')

class BookingNotificationInline(admin.TabularInline):
    model = BookingNotification
    extra = 0
    readonly_fields = ('notification_type', 'message', 'is_read', 'created_at')
    can_delete = False

def mark_as_confirmed(modeladmin, request, queryset):
    updated = queryset.update(status=BookingStatus.CONFIRMED)
    modeladmin.message_user(request, _(f"{updated} bookings marked as confirmed."))
mark_as_confirmed.short_description = _("Mark selected bookings as Confirmed")

def mark_as_cancelled(modeladmin, request, queryset):
    updated = queryset.update(status=BookingStatus.CANCELLED)
    modeladmin.message_user(request, _(f"{updated} bookings marked as cancelled."))
mark_as_cancelled.short_description = _("Mark selected bookings as Cancelled")

def mark_as_completed(modeladmin, request, queryset):
    updated = queryset.update(status=BookingStatus.COMPLETED)
    modeladmin.message_user(request, _(f"{updated} bookings marked as completed."))
mark_as_completed.short_description = _("Mark selected bookings as Completed")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'service', 'provider', 'start_time', 'colored_status', 'is_paid')
    list_filter = ('status', 'is_paid', 'service', 'provider', 'start_time')
    search_fields = ('customer__email', 'customer__first_name', 'customer__last_name', 'service__name', 'provider__email')
    date_hierarchy = 'start_time'
    inlines = [BookingPaymentInline, BookingNotificationInline]
    ordering = ('-start_time',)
    readonly_fields = ('created_at', 'updated_at')
    actions = [mark_as_confirmed, mark_as_cancelled, mark_as_completed]

    def colored_status(self, obj):
        color_map = {
            BookingStatus.PENDING: 'orange',
            BookingStatus.CONFIRMED: 'green',
            BookingStatus.CANCELLED: 'red',
            BookingStatus.COMPLETED: 'blue',
            BookingStatus.NO_SHOW: 'gray',
        }
        color = color_map.get(obj.status, 'black')
        return format_html('<span style="color: {};"><b>{}</b></span>', color, obj.get_status_display())
    colored_status.short_description = _('Status')

@admin.register(BookingPayment)
class BookingPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking', 'amount', 'currency', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'currency')
    search_fields = ('booking__customer__email', 'transaction_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(BookingNotification)
class BookingNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'booking', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__email', 'booking__service__name', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',) 