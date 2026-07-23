from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Milestone
from notifications.models import Notification

