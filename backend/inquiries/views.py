# inquiries/views.py

import logging
from rest_framework import generics, permissions

from users.permissions import IsAdmin
from .models import Inquiry
from .serializers import InquirySerializer, InquiryDetailSerializer

logger = logging.getLogger(__name__)


class InquiryCreateView(generics.CreateAPIView):
    """
    POST /api/inquiries/
    Koi bhi visitor submit kar sakta hai
    """
    serializer_class   = InquirySerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        inquiry = serializer.save()
        logger.info(f"New inquiry from: {inquiry.email}")


class InquiryListView(generics.ListAPIView):
    """
    GET /api/inquiries/
    Sirf admin dekh sakta hai
    """
    serializer_class   = InquiryDetailSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        queryset = Inquiry.objects.all()

        # Status se filter — /api/inquiries/?status=new
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset


class InquiryDetailView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/inquiries/<id>/  → Detail
    PATCH /api/inquiries/<id>/  → Status update
    Sirf admin
    """
    serializer_class   = InquiryDetailSerializer
    permission_classes = [IsAdmin]
    queryset           = Inquiry.objects.all()