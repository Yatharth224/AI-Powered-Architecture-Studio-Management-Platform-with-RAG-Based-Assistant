from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Milestone
from notifications.models import Notification


@receiver(post_save, sender=Milestone)
def notify_on_milestone_update(sender, instance, created, **kwargs):
    project = instance.project

    if created:
        message = f"New milestone '{instance.title}' added to {project.title}"
    else:
        message = f"Milestone '{instance.title}' updated to {instance.status}"
