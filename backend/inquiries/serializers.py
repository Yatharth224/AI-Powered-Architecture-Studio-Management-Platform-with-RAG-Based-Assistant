# inquiries/serializers.py

from rest_framework import serializers
from .models import Inquiry


class InquirySerializer(serializers.ModelSerializer):
    """Visitor form submit karne ke liye"""

    class Meta:
        model  = Inquiry
        fields = ['id', 'name', 'email', 'phone', 'subject', 'message']
        # Notice: status field nahi hai — visitor set nahi kar sakta


class InquiryDetailSerializer(serializers.ModelSerializer):
    """Admin ke liye — status bhi dikhega aur update ho sakega"""

    class Meta:
        model  = Inquiry
        fields = [
            'id', 'name', 'email', 'phone',
            'subject', 'message', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'name', 'email', 'phone', 'subject', 'message', 'created_at']
        # Sirf status admin change kar sakta hai