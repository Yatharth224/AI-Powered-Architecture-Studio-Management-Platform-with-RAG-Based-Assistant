# notifications/views.py

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(generics.ListAPIView):
    """
    GET /api/notifications/
    Apni notifications dekho
    """
    serializer_class   = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Sirf apni notifications — kisi aur ki nahi
        return Notification.objects.filter(user=self.request.user)


class MarkAsReadView(APIView):
    """
    PATCH /api/notifications/<id>/read/
    Notification ko read mark karo
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            # Sirf apni notification update kar sake — dusre ki nahi
            notification = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        notification.is_read = True
        notification.save()

        return Response({
            'message': 'Marked as read',
            'notification': NotificationSerializer(notification).data
        })


class MarkAllAsReadView(APIView):
    """
    PATCH /api/notifications/read-all/
    Saari notifications ek saath read mark karo
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True)
        # .update() — bulk update, ek query mein sab update ho jaate hain
        # Har record fetch karke save() karne se FASTER hai

        return Response({
            'message': f'{count} notifications marked as read'
        })


class NotificationDeleteView(generics.DestroyAPIView):
    """
    DELETE /api/notifications/<id>/
    """
    serializer_class   = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Sirf apni notification delete kar sake
        return Notification.objects.filter(user=self.request.user)