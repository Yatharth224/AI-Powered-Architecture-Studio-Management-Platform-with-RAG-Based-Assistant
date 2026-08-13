# ai_assistant/views.py

import uuid
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.throttling import AnonRateThrottle

from .models import ChatSession, ChatMessage
from .rag_engine import (
    build_knowledge_base,
    build_faiss_index,
    search_knowledge_base,
    generate_answer,
)

logger = logging.getLogger(__name__)

# Global variables — index aur chunks EK BAAR banenge
# server start hone par, HAR request pe DOBARA nahi
_index = None
_chunks = None


def get_rag_index():
    """
    Index sirf EK BAAR banao (server start hone par
    ya pehli request pe), phir REUSE karo
    """
    global _index, _chunks
    if _index is None:
        chunks = build_knowledge_base()
        _index, _chunks = build_faiss_index(chunks)
    return _index, _chunks


class ChatRateThrottle(AnonRateThrottle):
    rate = '20/minute'
    # Chatbot spam se bachane ke liye


class ChatView(APIView):
    """
    POST /api/ai/chat/
    Body: {
        "message": "Show me residential projects",
        "session_id": "optional-existing-session-id"
    }
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes   = [ChatRateThrottle]

    def post(self, request):
        message = request.data.get('message', '').strip()
        session_id = request.data.get('session_id')

        if not message:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Session dhundo ya naya banao
        if session_id:
            session, _ = ChatSession.objects.get_or_create(
                session_id=session_id,
                defaults={'user': request.user if request.user.is_authenticated else None}
            )
        else:
            session = ChatSession.objects.create(
                user=request.user if request.user.is_authenticated else None
            )

        # User ka message save karo
        ChatMessage.objects.create(
            session=session,
            role='user',
            message=message
        )

        # RAG pipeline chalao
        index, chunks = get_rag_index()
        results = search_knowledge_base(message, index, chunks)
        result = generate_answer(message, results)

        # AI ka jawab save karo
        ChatMessage.objects.create(
            session=session,
            role='assistant',
            message=result['answer']
        )

        logger.info(f"Chat query: '{message}' | Session: {session.session_id}")

        return Response({
            'session_id': str(session.session_id),
            'answer': result['answer'],
            'images': result['images'],
        })


class ChatHistoryView(APIView):
    """
    GET /api/ai/chat/history/?session_id=xxx
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        session_id = request.query_params.get('session_id')

        if not session_id:
            return Response(
                {'error': 'session_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = ChatSession.objects.get(session_id=session_id)
        except ChatSession.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        messages = session.messages.all().order_by('created_at')

        return Response({
            'session_id': str(session.session_id),
            'messages': [
                {'role': m.role, 'message': m.message, 'created_at': m.created_at}
                for m in messages
            ]
        })