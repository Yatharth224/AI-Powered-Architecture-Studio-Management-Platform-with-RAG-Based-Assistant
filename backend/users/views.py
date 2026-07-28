# users/views.py

import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import ArchitectInvite
from .permissions import IsAdmin
from .serializers import (
    ClientRegisterSerializer,
    UserProfileSerializer,
    UserListSerializer,
    UpdateRoleSerializer,
    ArchitectInviteSerializer,
    ArchitectRegisterSerializer,
)

User = get_user_model()
logger = logging.getLogger(__name__)
# Logger kya karta hai:
# Har request ka record rakhta hai
# Production mein debugging ke liye useful


# ----------------------------
# THROTTLE CLASSES
# OWASP A07 - Brute force se bachao
# ----------------------------

class LoginRateThrottle(AnonRateThrottle):
    """
    Anonymous users ke liye rate limit
    10000 requests handle karne ke liye
    login pe strict limit
    """
    rate = '5/minute'
    # 1 minute mein sirf 5 login attempts
    # Brute force attack se bachata hai


class RegisterRateThrottle(AnonRateThrottle):
    rate = '3/minute'
    # Spam registrations rokta hai


# ----------------------------
# CUSTOM JWT - Role token mein add karo
# OWASP A01 - Access Control
# ----------------------------

class CustomTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Extra data token mein add karo
        # Frontend ko role pata chalega
        token['role']     = user.role
        token['email']    = user.email
        token['username'] = user.username
        return token


class CustomLoginView(TokenObtainPairView):
    """
    POST /api/auth/login/
    Body: { "email": "...", "password": "..." }

    OWASP A07: Rate limiting applied
    """
    serializer_class = CustomTokenSerializer
    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Successful login log karo
            logger.info(f"Login successful: {request.data.get('email')} | IP: {self.get_client_ip(request)}")
        else:
            # Failed login log karo - OWASP A09
            logger.warning(f"Login failed: {request.data.get('email')} | IP: {self.get_client_ip(request)}")

        return response

    def get_client_ip(self, request):
        # Real IP address nikalo
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0]
        return request.META.get('REMOTE_ADDR')


# ----------------------------
# CLIENT REGISTRATION
# ----------------------------

class ClientRegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/client/
    Body: {
        "email": "...",
        "username": "...",
        "password": "...",
        "confirm_password": "...",
        "phone": "..."
    }
    Anyone can register as client
    """
    serializer_class   = ClientRegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes   = [RegisterRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Registration ke baad auto login
        refresh = RefreshToken.for_user(user)

        logger.info(f"New client registered: {user.email}")

        return Response({
            'message': 'Account created successfully',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access':  str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)


# ----------------------------
# LOGOUT
# OWASP A07 - Token invalidate karo
# ----------------------------

class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Header: Authorization: Bearer <access_token>
    Body: { "refresh": "<refresh_token>" }

    Refresh token blacklist ho jaata hai
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')

            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()
            # Token blacklist mein chala gaya
            # Ab ye token kaam nahi karega

            logger.info(f"Logout: {request.user.email}")

            return Response(
                {'message': 'Logged out successfully'},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


# ----------------------------
# PROFILE
# ----------------------------

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/auth/profile/  - apna profile dekho
    PUT  /api/auth/profile/  - apna profile update karo
    Header: Authorization: Bearer <token>
    """
    serializer_class   = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Sirf apna profile milega
        # Doosre ka nahi - OWASP A01
        return self.request.user


# ----------------------------
# ADMIN - USER LIST
# OWASP A01 - Sirf admin dekh sakta hai
# ----------------------------

class UserListView(generics.ListAPIView):
    """
    GET /api/auth/users/
    Header: Authorization: Bearer <admin_token>

    Only admin can access
    """
    serializer_class   = UserListSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        queryset = User.objects.all().order_by('-created_at')

        # Filtering support - query params se
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        # Example: /api/auth/users/?role=client
        # Sirf clients dikhenge

        return queryset


# ----------------------------
# ADMIN - ROLE UPDATE
# OWASP A01 - Sirf admin role change kar sakta hai
# ----------------------------

class UpdateUserRoleView(APIView):
    """
    PATCH /api/auth/users/<user_id>/role/
    Header: Authorization: Bearer <admin_token>
    Body: { "role": "client" }

    Only admin can change roles
    """
    permission_classes = [IsAdmin]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Admin khud ko degrade na kar sake
        if user == request.user:
            return Response(
                {'error': 'You cannot change your own role'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UpdateRoleSerializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger.info(
            f"Role updated: {user.email} → {request.data.get('role')} "
            f"by {request.user.email}"
        )

        return Response({
            'message': 'Role updated successfully',
            'user': UserListSerializer(user).data
        })


# ----------------------------
# ARCHITECT INVITE
# OWASP A01 - Sirf admin invite kar sakta hai
# ----------------------------

class InviteArchitectView(APIView):
    """
    POST /api/auth/invite/architect/
    Header: Authorization: Bearer <admin_token>
    Body: { "email": "architect@test.com" }
    """
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = ArchitectInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invite = serializer.save()

        # Real project mein email bhejo
        # Abhi ke liye token return karo
        invite_link = f"http://localhost:3000/register/architect/?token={invite.token}"

        logger.info(
            f"Architect invite sent: {invite.email} "
            f"by admin {request.user.email}"
        )

        return Response({
            'message': f'Invite sent to {invite.email}',
            'invite_link': invite_link,
            'expires_at': invite.expires_at,
        }, status=status.HTTP_201_CREATED)


# ----------------------------
# ARCHITECT REGISTER
# ----------------------------

class ArchitectRegisterView(APIView):
    """
    POST /api/auth/register/architect/
    Body: {
        "token": "uuid-here",
        "username": "...",
        "password": "...",
        "confirm_password": "..."
    }
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes   = [RegisterRateThrottle]

    def post(self, request):
        serializer = ArchitectRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invite = serializer.validated_data['invite']

        
        user = User.objects.create_user(
            email    = invite.email,
            username = serializer.validated_data['username'],
            password = serializer.validated_data['password'],
            role     = 'architect'
        )

        # Invite use hua mark karo
        invite.is_used = True
        invite.save()

        
        refresh = RefreshToken.for_user(user)

        logger.info(f"New architect registered: {user.email}")

        return Response({
            'message': 'Architect account created successfully',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access':  str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)