from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import DocumentChunk, ChatbotTopic, Document, LegalPage
from .services import ChatbotService
from django.views.decorators.http import require_POST, require_GET
from django.utils.translation import get_language
from django.core.files.storage import default_storage
import json
from django.shortcuts import render, get_object_or_404

class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Welcome to SalonManager')
        return context

@method_decorator(csrf_exempt, name='dispatch')
class ChatbotRAGView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        question = data.get('question', '').lower()
        # Simple search: find chunk with most keyword overlap
        best_chunk = ''
        best_score = 0
        for chunk in DocumentChunk.objects.all():
            score = sum(1 for word in question.split() if word in chunk.chunk.lower())
            if score > best_score:
                best_score = score
                best_chunk = chunk.chunk
        if not best_chunk:
            best_chunk = _('No relevant information found in the document.')
        return JsonResponse({'answer': best_chunk})

@csrf_exempt
@require_POST
def api_chat(request):
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        if not question:
            return JsonResponse({'success': False, 'error': 'No question provided.'}, status=400)
        service = ChatbotService()
        answer = service.generate_answer(question)
        return JsonResponse({'success': True, 'answer': answer})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_GET
def api_topics(request):
    lang = request.GET.get('lang') or get_language() or 'en'
    topics = ChatbotTopic.objects.filter(language=lang, is_active=True).order_by('order', 'label')
    data = [
        {'label': t.label, 'question': t.question, 'order': t.order} for t in topics
    ]
    return JsonResponse({'success': True, 'topics': data})

@csrf_exempt
@require_POST
def api_upload(request):
    try:
        file = request.FILES.get('document')
        if not file or not file.name.lower().endswith('.pdf'):
            return JsonResponse({'success': False, 'error': 'Only PDF files are allowed.'}, status=400)
        doc = Document.objects.create(title=file.name, file=file)
        # If signals are set up, chunking will be triggered automatically
        return JsonResponse({'success': True, 'message': 'Document uploaded successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def legal_page(request, page_type):
    lang = request.LANGUAGE_CODE
    page = get_object_or_404(LegalPage, page_type=page_type, language=lang)
    return render(request, 'core/legal_page.html', {'page': page}) 