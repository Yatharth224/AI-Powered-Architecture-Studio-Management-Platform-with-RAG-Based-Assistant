from django.db import models
from django.conf import settings




class Document(models.Model):

    class FileType(models.TextChoices):
        BLUEPRINT = 'blueprint', 'Blueprint'
        CONTRACT  = 'contract',  'Contract'
        REPORT    = 'report',    'Report'
        MODEL_3D  = '3d_model',  '3D Model'
        OTHER     = 'other',     'Other'

    project = models.ForeignKey(
        'projects.Project',
        
        on_delete=models.CASCADE,
        related_name='documents'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    title       = models.CharField(max_length=200)
    file        = models.FileField(upload_to='documents/%Y/%m/')
    file_type   = models.CharField(max_length=20, choices=FileType.choices, default=FileType.OTHER)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'documents'

    def __str__(self):
        return self.title