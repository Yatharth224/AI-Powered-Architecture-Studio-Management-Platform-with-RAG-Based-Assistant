# projects/models.py

from django.db import models
from django.conf import settings


class Project(models.Model):

    class Status(models.TextChoices):
        PLANNING    = 'planning',    'Planning'
        IN_PROGRESS = 'in_progress', 'In Progress'
        ON_HOLD     = 'on_hold',     'On Hold'
        COMPLETED   = 'completed',   'Completed'
        CANCELLED   = 'cancelled',   'Cancelled'

    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status      = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNING)
    budget      = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    location    = models.CharField(max_length=255, blank=True)

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='client_projects'
       
    )

    architect = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='architect_projects'
    )

    start_date = models.DateField(null=True, blank=True)
    end_date   = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']  # latest pehle

    def __str__(self):
        return self.title


class Milestone(models.Model):

    class Status(models.TextChoices):
        PENDING     = 'pending',     'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED   = 'completed',   'Completed'

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        
        related_name='milestones'
    )

    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status      = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    due_date    = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'milestones'

    def __str__(self):
        return f"{self.project.title} → {self.title}"