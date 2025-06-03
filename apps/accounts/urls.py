from django.urls import path
from .views import ProfileView

urlpatterns = [
    # ... alte url-uri ...
    path('profile/', ProfileView.as_view(), name='account_profile'),
] 