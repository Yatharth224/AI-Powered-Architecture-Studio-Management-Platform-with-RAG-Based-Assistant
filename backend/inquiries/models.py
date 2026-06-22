from django.db import models



class Inquiry(models.Model):

    class Status(models.TextChoices):
        NEW       = 'new',       'New'
        CONTACTED = 'contacted', 'Contacted'
        CONVERTED = 'converted', 'Converted'
        CLOSED    = 'closed',    'Closed'

    name       = models.CharField(max_length=100)
    email      = models.EmailField()
    phone      = models.CharField(max_length=15, blank=True)
    subject    = models.CharField(max_length=200)
    message    = models.TextField()
    status     = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"