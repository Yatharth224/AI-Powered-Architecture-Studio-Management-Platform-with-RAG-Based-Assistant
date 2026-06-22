from django.db import models


from django.db import models


class Service(models.Model):

    class Category(models.TextChoices):
        RESIDENTIAL = 'residential', 'Residential'
        COMMERCIAL  = 'commercial',  'Commercial'
        INTERIOR    = 'interior',    'Interior'
        LANDSCAPE   = 'landscape',   'Landscape'

    title       = models.CharField(max_length=200)
    description = models.TextField()
    category    = models.CharField(max_length=20, choices=Category.choices)
    price_range = models.CharField(max_length=100, blank=True)
    image       = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'services'

    def __str__(self):
        return self.title