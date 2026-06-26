# ai_assistant/models.py

import uuid
from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='chat_sessions'
    )
    session_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )                                    # ← bracket band
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_sessions'

    def __str__(self):
        return str(self.session_id)      # ← str() wrap


class ChatMessage(models.Model):

    class Role(models.TextChoices):
        USER      = 'user',      'User'
        ASSISTANT = 'assistant', 'Assistant'

    session    = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role       = models.CharField(max_length=20, choices=Role.choices)
    message    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']


class AIRequirement(models.Model):
    project = models.OneToOneField(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='ai_requirement'
    )
    raw_input           = models.TextField()
    property_type       = models.CharField(max_length=100, blank=True)
    plot_size           = models.CharField(max_length=100, blank=True)
    budget_range        = models.CharField(max_length=100, blank=True)
    architectural_style = models.CharField(max_length=100, blank=True)
    num_rooms           = models.IntegerField(null=True, blank=True)
    ai_analysis         = models.JSONField(default=dict)
    created_at          = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_requirements'

    def __str__(self):
        return f"AI Analysis - {self.project.title}"