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


class LoginRateThrottle(AnonRateThrottle):
    rate = '5/minute'

class RegisterRateThrottle(AnonRateThrottle):
    rate = '3/minute'    



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