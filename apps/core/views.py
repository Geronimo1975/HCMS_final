from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import DocumentChunk
import json

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