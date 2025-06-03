from django.urls import path
from .views import CookieConsentView, legal_page

urlpatterns = [
    path('cookie-consent/', CookieConsentView.as_view(), name='cookie-consent'),
    path('privacy/', legal_page, {'doc_type': 'privacy'}, name='privacy'),
    path('terms/', legal_page, {'doc_type': 'terms'}, name='terms'),
    path('impressum/', legal_page, {'doc_type': 'impressum'}, name='impressum'),
] 