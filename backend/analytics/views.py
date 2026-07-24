
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response

from users.permissions import IsAdmin
from projects.models import Project, Milestone
from inquiries.models import Inquiry
from users.models import User