# documents/serializers.py

from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(
        source='uploaded_by.username',
        read_only=True
    )
    project_title = serializers.CharField(
        source='project.title',
        read_only=True
    )

    class Meta:
        model  = Document
        fields = [
            'id',
            'project',
            'project_title',
            'uploaded_by',
            'uploaded_by_name',
            'title',
            'file',
            'file_type',
            'created_at'
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_at']

    def validate_file(self, value):
        # File size check karo — 10 MB se zyada nahi
        max_size = 10 * 1024 * 1024  # 10 MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(
                "File size 10 MB se zyada nahi honi chahiye"
            )

        # File extension check karo
        allowed_extensions = [
            '.pdf', '.jpg', '.jpeg', '.png',
            '.dwg', '.glb', '.gltf', '.docx'
        ]
        file_name = value.name.lower()
        if not any(file_name.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f"Sirf ye files allowed hain: {', '.join(allowed_extensions)}"
            )

        return value