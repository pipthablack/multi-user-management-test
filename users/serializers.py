
from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration. Validates and creates new user instances.
    """
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2')

    def validate(self, attrs):
        """
        Validates the registration data. Checks if passwords match, email is unique, and username meets requirements.
        """
        # Passwords must match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        # Check if email is already used
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "This email is already in use."})

        # Validate username (e.g., length or format)
        if len(attrs['username']) < 3:
            raise serializers.ValidationError({"username": "Username must be at least 3 characters long."})

        return attrs
    
    def validate_email(self, value):
        """
        Validates the email domain. Only allows specific domains.
        """
        allowed_domains = ['gmail.com', 'yahoo.com', 'email.com']
        domain = value.split('@')[-1]
        if domain not in allowed_domains:
            raise serializers.ValidationError("Email domain is not allowed. Only @gmail.com, @yahoo.com, or @email.com are accepted.")
        return value
    
    def validate_username(self, value):
        """
        Validates the username. Only allows alphanumeric characters.
        """
        # Additional username validation (e.g., no special characters)
        if not value.isalnum():
            raise serializers.ValidationError("Username must only contain alphanumeric characters.")
        return value

    def create(self, validated_data):
        """
        Creates a new user instance after removing the 'password2' field from the validated data.
        """
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login. Validates email and password, and returns user tokens if successful.
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        """
        Validates the login data. Authenticates the user and returns their email, username, and tokens if successful.
        """
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(email=email, password=password)
        if user and user.is_active:
            return {
                'email': user.email,
                'username': user.username,
                'tokens': user.tokens(),
            }
        raise serializers.ValidationError("Invalid credentials")