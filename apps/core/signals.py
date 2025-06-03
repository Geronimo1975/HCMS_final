from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Document, DocumentChunk
import PyPDF2

@receiver(post_save, sender=Document)
def process_pdf_chunks(sender, instance, created, **kwargs):
    if not created:
        return
    # Clear old chunks if any
    instance.chunks.all().delete()
    # Extract text from PDF
    pdf_path = instance.file.path
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        full_text = "\n".join(page.extract_text() or '' for page in reader.pages)
    # Split into paragraphs (by double newlines)
    paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]
    for idx, para in enumerate(paragraphs):
        DocumentChunk.objects.create(document=instance, chunk=para, order=idx) 