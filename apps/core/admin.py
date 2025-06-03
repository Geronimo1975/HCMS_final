from django.contrib import admin
from .models import Document, DocumentChunk, ChatbotTopic, LegalPage

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'file', 'uploaded_at')
    search_fields = ('title',)
    ordering = ('-uploaded_at',)

@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('document', 'order')
    search_fields = ('chunk',)
    ordering = ('document', 'order')

@admin.register(ChatbotTopic)
class ChatbotTopicAdmin(admin.ModelAdmin):
    list_display = ('label', 'language', 'order', 'is_active')
    list_filter = ('language', 'is_active')
    search_fields = ('label', 'question')
    ordering = ('language', 'order', 'label')

@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    list_display = ('page_type', 'title', 'language')
    list_filter = ('page_type', 'language')
    search_fields = ('title', 'content') 