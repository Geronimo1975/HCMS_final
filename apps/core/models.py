from django.db import models
from django.utils.translation import gettext_lazy as _

class Document(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    file = models.FileField(_('PDF File'), upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class DocumentChunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk = models.TextField(_('Chunk'))
    order = models.PositiveIntegerField(_('Order'), default=0)

    def __str__(self):
        return f"{self.document.title} - Chunk {self.order}"

class ChatbotTopic(models.Model):
    label = models.CharField(_('Button Label'), max_length=100)
    question = models.CharField(_('Question'), max_length=255)
    language = models.CharField(_('Language'), max_length=10, choices=[('ro', 'Română'), ('en', 'English'), ('de', 'Deutsch')], default='ro')
    order = models.PositiveIntegerField(_('Order'), default=0)
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        ordering = ['language', 'order', 'label']
        verbose_name = _('Chatbot Topic')
        verbose_name_plural = _('Chatbot Topics')

    def __str__(self):
        return f"{self.label} ({self.language})" 