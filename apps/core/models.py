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