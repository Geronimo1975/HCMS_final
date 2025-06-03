from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import UserConsent, LegalDocumentVersion

# Create your views here.

class CookieConsentView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        session_key = request.session.session_key or request.session.save() or request.session.session_key
        consent, created = UserConsent.objects.get_or_create(
            session_key=session_key,
            defaults={
                'essential': data.get('essential', True),
                'analytics': data.get('analytics', False),
                'marketing': data.get('marketing', False),
                'preferences': data.get('preferences', False),
            }
        )
        if not created:
            consent.essential = data.get('essential', True)
            consent.analytics = data.get('analytics', False)
            consent.marketing = data.get('marketing', False)
            consent.preferences = data.get('preferences', False)
            consent.save()
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)

def legal_page(request, doc_type):
    lang = request.LANGUAGE_CODE
    doc = LegalDocumentVersion.objects.filter(doc_type=doc_type, language=lang).order_by('-published_at').first()
    return render(request, f'legal/{doc_type}.html', {'doc': doc})
