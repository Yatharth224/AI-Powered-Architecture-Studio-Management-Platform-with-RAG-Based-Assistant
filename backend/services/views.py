# services/views.py

import logging
from rest_framework import generics, permissions

from users.permissions import IsAdmin
from .models import Service
from .serializers import ServiceSerializer

logger = logging.getLogger(__name__)


class ServiceListView(generics.ListCreateAPIView):
    """
    GET  /api/services/  → Public, sab dekh sakte hain
    POST /api/services/  → Sirf Admin
    """
    serializer_class = ServiceSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdmin()]
        # GET ke liye koi bhi dekh sakta hai — visitor bhi
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True)

        # Category se filter — /api/services/?category=residential
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        return queryset

    def perform_create(self, serializer):
        service = serializer.save()
        logger.info(f"Service created: {service.title} by {self.request.user.email}")


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/services/<id>/  → Public
    PUT    /api/services/<id>/  → Admin only
    DELETE /api/services/<id>/  → Admin only
    """
    serializer_class = ServiceSerializer
    queryset         = Service.objects.all()

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [IsAdmin()]