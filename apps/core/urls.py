from django.urls import path
from . import views
from .views import api_chat, api_topics, api_upload, legal_page

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('api/chatbot/', views.ChatbotRAGView.as_view(), name='chatbot_rag'),
    path('api/chat/', api_chat, name='api_chat'),
    path('api/topics/', api_topics, name='api_topics'),
    path('api/upload/', api_upload, name='api_upload'),
    path('impressum/', legal_page, {'page_type': 'impressum'}, name='impressum'),
    path('privacy/', legal_page, {'page_type': 'privacy'}, name='privacy'),
    path('terms/', legal_page, {'page_type': 'terms'}, name='terms'),
] 