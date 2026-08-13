# ai_assistant/urls.py

from django.urls import path
from .views import ChatView, ChatHistoryView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='ai_chat'),
    path('chat/history/', ChatHistoryView.as_view(), name='chat_history'),
]