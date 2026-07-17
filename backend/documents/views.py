# documents/views.py

import logging
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from projects.models import Project
from .models import Document
from .serializers import DocumentSerializer

logger = logging.getLogger(__name__)


class DocumentListView(generics.ListCreateAPIView):
    """
    GET  /api/documents/  → Documents list
    POST /api/documents/  → Document upload
    """
    serializer_class   = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    # File upload ke liye ye parsers chahiye
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        queryset = Document.objects.all()

        # Role based filtering — OWASP A01
        if user.role == 'admin':
            pass  # sab dikhega
        elif user.role == 'client':
            # Sirf apne project ke documents
            queryset = queryset.filter(project__client=user)
        elif user.role == 'architect':
            # Sirf assigned project ke documents
            queryset = queryset.filter(project__architect=user)
        else:
            queryset = Document.objects.none()

        # Project ID se filter karne ka option
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        return queryset

    def perform_create(self, serializer):
        # Kisne upload kiya — automatically set karo
        document = serializer.save(uploaded_by=self.request.user)
        logger.info(
            f"Document uploaded: {document.title} "
            f"by {self.request.user.email}"
        )


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    """
    GET    /api/documents/<id>/  → Document detail
    DELETE /api/documents/<id>/  → Document delete
    """
    serializer_class   = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Document.objects.all()
        elif user.role == 'client':
            return Document.objects.filter(project__client=user)
        elif user.role == 'architect':
            return Document.objects.filter(project__architect=user)
        return Document.objects.none()

    def destroy(self, request, *args, **kwargs):
        document = self.get_object()

        # Sirf jisne upload kiya ya admin delete kar sake
        if request.user.role != 'admin' and document.uploaded_by != request.user:
            return Response(
                {'error': 'You do not have permission to delete this'},
                status=status.HTTP_403_FORBIDDEN
            )

        logger.info(f"Document deleted: {document.title} by {request.user.email}")
        return super().destroy(request, *args, **kwargs)