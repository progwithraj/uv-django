from .models import MyUser
from rest_framework import serializers

class MyUserModelSerializer(serializers.ModelSerializer):
    class Meta:
        visible_fields = [
            'id',
            'email',
            'username',
            'password',
            'is_superuser',
            'phone',
            'dept',
            'is_staff',
            'is_active',
        ]
        model = MyUser
        fields = visible_fields
        extra_kwargs = {
            'email': {
                'required': True,
                'error_messages': {
                    'required': 'Email address is required',
                    'blank': 'Email address cannot be blank',
                    'unique': 'Email address already exists'  # Add this
                }
            },
            'username': {
                'required': True,
                'error_messages': {
                    'required': 'Username is required',
                    'blank': 'Username cannot be blank',
                    'unique': 'Username already exists'  # Add this
                }
            },
            'password': {
                'write_only': True,
                'required': True,
                'error_messages': {
                    'required': 'Password is required',
                    'blank': 'Password cannot be blank',
                }
            }
        }

    def validate_email(self, value):
        """Validate email"""
        if not value:
            raise serializers.ValidationError('Email address is required')
        if MyUser.objects.filter(email=value.lower()).exists():  # Add .lower()
            raise serializers.ValidationError('Email address already exists')
        return value.lower()  # Normalize email to lowercase

    def validate_username(self, value):
        """Validate username"""
        if not value:
            raise serializers.ValidationError('Username is required')
        if MyUser.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists')
        return value
    
    def validate_password(self, value):
        """Validate password"""
        if not value:
            raise serializers.ValidationError('Password is required')
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long')
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = MyUser(**validated_data)
        if password is not None:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password is not None:
            user.set_password(password)
            user.save()
        return user
