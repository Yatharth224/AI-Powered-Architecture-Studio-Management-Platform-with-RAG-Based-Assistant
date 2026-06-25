

import uuid
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from .managers import UserManager


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN     = 'admin',     'Admin'
        ARCHITECT = 'architect', 'Architect'
        CLIENT    = 'client',    'Client'
        VISITOR   = 'visitor',   'Visitor'

    email = models.EmailField(unique=True)
    role  = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VISITOR
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Invalid phone number. Example: +919876543210'
            )
        ]
    )

    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
       
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.email} ({self.role})"


class ArchitectInvite(models.Model):

    
    email = models.EmailField()

    token      = models.UUIDField(default=uuid.uuid4, unique=True)
    is_used    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'architect_invites'
        constraints = [
            models.UniqueConstraint(
                fields=['email'],
                condition=models.Q(is_used=False),
                name='unique_pending_invite'
            )
        ]

    def save(self, *args, **kwargs):
       
        if not self.expires_at:
            from django.utils import timezone
            from datetime import timedelta
            self.expires_at = timezone.now() + timedelta(hours=48)
        super().save(*args, **kwargs)

    def is_valid(self):
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()

    def __str__(self):
        return f"{self.email} - {'Used' if self.is_used else 'Pending'}"