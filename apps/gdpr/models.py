from django.db import models
from django.conf import settings

# Create your models here.

class UserConsent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=64, null=True, blank=True)
    essential = models.BooleanField(default=True)
    analytics = models.BooleanField(default=False)
    marketing = models.BooleanField(default=False)
    preferences = models.BooleanField(default=False)
    consent_date = models.DateTimeField(auto_now_add=True)
    withdrawn = models.BooleanField(default=False)
    withdrawn_date = models.DateTimeField(null=True, blank=True)

class CookiePreference(models.Model):
    user_consent = models.ForeignKey(UserConsent, on_delete=models.CASCADE)
    cookie_name = models.CharField(max_length=128)
    accepted = models.BooleanField(default=False)

LEGAL_TEMPLATES = {
    ('privacy', 'de'): "Hier steht Ihre deutsche Datenschutzerklärung...",
    ('privacy', 'en'): "This is your English privacy policy...",
    ('terms', 'de'): "Hier stehen Ihre deutschen AGB...",
    ('terms', 'en'): "These are your English terms and conditions...",
    ('impressum', 'de'): "Ihr Impressum mit Firmenangaben...",
    ('impressum', 'en'): "Your legal notice with company details...",
}

class LegalDocumentVersion(models.Model):
    doc_type = models.CharField(max_length=32, choices=[('privacy', 'Privacy Policy'), ('terms', 'Terms & Conditions'), ('impressum', 'Impressum')])
    language = models.CharField(max_length=2, choices=[('de', 'German'), ('en', 'English')])
    content = models.TextField()
    version = models.CharField(max_length=16)
    published_at = models.DateTimeField(auto_now_add=True)

    def fill_with_template(self):
        self.content = LEGAL_TEMPLATES.get((self.doc_type, self.language), "")

class GDPRRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=32, choices=[('export', 'Data Export'), ('delete', 'Account Deletion'), ('portability', 'Data Portability'), ('withdraw', 'Consent Withdrawal')])
    status = models.CharField(max_length=16, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('rejected', 'Rejected')], default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    details = models.TextField(blank=True)
