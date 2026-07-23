from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Milestone
from notifications.models import Notification


@receiver(post_save, sender=Milestone)
def notify_on_milestone_update(sender, instance, created, **kwargs):