from django.urls import path
from . import views
from .views import BookingListView

app_name = 'bookings'

urlpatterns = [
    path('', BookingListView.as_view(), name='bookings'),
    path('', views.BookingListView.as_view(), name='list'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='detail'),
    path('create/', views.BookingCreateView.as_view(), name='create'),
    path(
        'create/<int:service_id>/',
        views.BookingCreateView.as_view(),
        name='create_for_service'
    ),
    path('<int:pk>/update/', views.BookingUpdateView.as_view(), name='update'),
    path('<int:pk>/cancel/', views.BookingCancelView.as_view(), name='cancel'),
    path('calendar/', views.BookingCalendarView.as_view(), name='calendar'),
    path(
        'api/calendar-events/',
        views.CalendarEventsView.as_view(),
        name='calendar_events'
    ),
    path(
        'api/available-slots/',
        views.get_available_slots,
        name='available_slots'
    ),
] 