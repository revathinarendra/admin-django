import os
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import UserProfile

Account = get_user_model()  # Correct user model reference

# 🔒 Signup Serializer
class SignUpSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=UserProfile.GENDER_CHOICES, required=True)
    phone_number = serializers.CharField(required=True)
    address_line_1 = serializers.CharField(required=False, allow_blank=True)
    address_line_2 = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Account
        fields = [
            "first_name", "last_name", "username", "email", "password", "confirm_password",
            "date_of_birth", "gender", "phone_number",
            "address_line_1", "address_line_2", "city", "state", "country", "profile_picture"
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 6},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        profile_data = {
            'date_of_birth': validated_data.pop('date_of_birth'),
            'gender': validated_data.pop('gender'),
            'phone_number': validated_data.pop('phone_number'),
            'address_line_1': validated_data.pop('address_line_1', ''),
            'address_line_2': validated_data.pop('address_line_2', ''),
            'city': validated_data.pop('city', ''),
            'state': validated_data.pop('state', ''),
            'country': validated_data.pop('country', ''),
            'profile_picture': validated_data.pop('profile_picture', None),
        }

        validated_data.pop('confirm_password')

        user = Account.objects.create_user(
            **validated_data,
            is_active=False  # Require email verification
        )

        UserProfile.objects.create(user=user, **profile_data)
        return user


# 🔐 Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        if not Account.objects.filter(email=email).exists():
            raise serializers.ValidationError("No user with this email.")
        return data


# 🔁 Password Reset (request)
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not Account.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user associated with this email.")
        return value


# 🔁 Password Reset (confirm)
class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=6)
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = Account.objects.get(pk=uid)
        except Exception:
            raise serializers.ValidationError("Invalid user or token")

        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError("Invalid or expired token")
        return data

    def save(self):
        uid = force_str(urlsafe_base64_decode(self.validated_data['uidb64']))
        user = Account.objects.get(pk=uid)
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


# 👤 Basic User Serializer (nested)
class UserProfileBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('date_of_birth', 'gender')


class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileBasicSerializer()

    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'email', 'userprofile')


# 👤 Full Profile Serializer
DEFAULT_IMAGE_URL = os.getenv(
    'DEFAULT_PROFILE_IMAGE_URL',
    'https://lhbowflyvxafohnsdvqf.supabase.co/storage/v1/object/public/images/default-user.png'
)

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    profile_picture = serializers.ImageField(read_only=True)
    google_data = serializers.SerializerMethodField()
    google_email = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            'user', 'email', 'google_email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'profile_picture', 'date_of_birth', 'gender',
            'address_line_1', 'address_line_2', 'city', 'state', 'country', 'google_data'
        ]
        read_only_fields = ['user', 'email']

    def get_email(self, obj):
        return obj.user.email

    def get_google_data(self, obj):
        return None  # Or implement logic

    def get_google_email(self, obj):
        return None  # Or implement logic

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not instance.profile_picture:
            rep['profile_picture'] = DEFAULT_IMAGE_URL
        else:
            rep['profile_picture'] = instance.profile_picture.url
        return rep

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
