
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ArchitectInvite

User = get_user_model()


class ArchitectInviteSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True,min_length=8)
    confirm_password = serializers.CharField(write_only=True)


    class Meta:
        model =User
        fields = [
            'email',
            'username',
            'password',
            'confirm_password',
            'phone'
        ]


    def validate_email(self,value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value.lower()
    

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data['role']='client'
        return User.objects.create_user(**validated_data)
    


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','username','role','phone','profile_picture','created_at']

        read_only_fields = ['id','email','role','created_at']


class UserListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model  = User
        fields = [
            'id',
            'email',
            'username',
            'role',
            'phone',
            'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'email', 'created_at']


class UpdateRoleSerializer(serializers.ModelSerializer):
   
    class Meta:
        model  = User
        fields = ['role']

    def validate_role(self, value):
        valid_roles = ['visitor', 'client', 'architect', 'admin']
        if value not in valid_roles:
            raise serializers.ValidationError("Invalid role")
        return value
    


class ArchitectInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchitectInvite
        fields = ['email']

    def validate_email(self, value):
        if ArchitectInvite.objects.filter(email=value,is_used=False).exists():
            raise serializers.ValidationError("An invite has already been sent to this email.")
        
        return value.lower()
    



class ArchitectRegisterSerializer(serializers.Serializer):
    
    token    = serializers.UUIDField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })

        
        try:
            invite = ArchitectInvite.objects.get(token=data['token'])
        except ArchitectInvite.DoesNotExist:
            raise serializers.ValidationError({
                  'token': 'Invalid invite link'
            })

        if not invite.is_valid():
            raise serializers.ValidationError({
                'token': 'This invitation link has expired or has already been used.'
            })

        
        data['invite'] = invite
        return data