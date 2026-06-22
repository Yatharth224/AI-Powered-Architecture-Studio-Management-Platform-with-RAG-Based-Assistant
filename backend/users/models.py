import uuid 
from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager
from django.utils import timezone
# Create your models here.


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN     = 'admin',     'Admin'
        ARCHITECT = 'architect', 'Architect'
        CLIENT    = 'client',    'Client'
        VISITOR   = 'visitor',   'Visitor'

    email           = models.EmailField(unique=True)
    role            = models.CharField(max_length=20, choices=Role.choices, default=Role.VISITOR)
    phone           = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    objects = UserManager()  # tumhara manager connect karo

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.email} ({self.role})"


class ArchitectInvite(models.Model):
    email       = models.EmailField(unique=True)
    token       = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_used     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    exprires_at  = models.DateTimeField()



    class Meta:
        db_table = 'architect_invites'

    def is_valid(self):

        return not self.is_used and self.exprires_at > timezone.now()
    
    def __str__(self):
        return f"Invite for {self.email} - {'Used' if self.is_used else 'Pending'}"