from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .models import UserProfile
import os



from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class SignUpSerializer(serializers.ModelSerializer):
    # UserProfile fields
    date_of_birth = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=UserProfile.GENDER_CHOICES, required=True)
    phone_number = serializers.CharField(required=True)
    address_line_1 = serializers.CharField(required=False, allow_blank=True)
    address_line_2 = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    state = serializers.CharField(required=False, allow_blank=True)
    country = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    # Extra password confirmation
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "username", "email", "password", "confirm_password",
            "date_of_birth", "gender", "phone_number",
            "address_line_1", "address_line_2", "city", "state", "country", "profile_picture"
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'password': {'write_only': True, 'required': True, 'min_length': 6},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        # Pop user profile fields
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
        email = validated_data['email']

        user = User.objects.create_user(
            username=validated_data.get("username", email),
            email=email,
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_active=False  # Until email verification
        )

        UserProfile.objects.create(user=user, **profile_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('date_of_birth', 'gender')

class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer()

    class Meta:
        model = User
           
        fields = ('first_name', 'last_name', 'email',  'userprofile')



class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is associated with this email address.")
        return value

class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=6)
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid token or user ID")
        
        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError("Invalid token")

        return data

    def save(self):
        uid = force_str(urlsafe_base64_decode(self.validated_data['uidb64']))
        user = User.objects.get(pk=uid)
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            if not User.objects.filter(email=email).exists():
                raise serializers.ValidationError('No user found with this email address.')

        return data



# Use environment variable for flexibility, or set it directly
DEFAULT_IMAGE_URL = os.getenv(
    'DEFAULT_PROFILE_IMAGE_URL', 
    'https://lhbowflyvxafohnsdvqf.supabase.co/storage/v1/object/public/images/default-user.png'
)



class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    phone_number = serializers.CharField()
    profile_picture = serializers.ImageField(read_only=True) 
    google_data = serializers.SerializerMethodField()
    google_email = serializers.SerializerMethodField()  # Set as read-only

    class Meta:
        model = UserProfile
        fields = [
            'user', 'email','google_email', 'first_name', 'last_name', 'full_name', 'phone_number',
            'profile_picture', 'date_of_birth', 'gender', 'address_line_1', 
            'address_line_2', 'city', 'state', 'country','google_data'
        ]
        read_only_fields = ['user', 'email']

    def get_email(self, obj):
        return obj.user.email  # Default Django user email

    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Use default image URL if profile_picture is not set
        if not instance.profile_picture:
            representation['profile_picture'] = DEFAULT_IMAGE_URL
        else:
            representation['profile_picture'] = instance.profile_picture.url
            
        return representation

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            # Update first_name and last_name on the user model
            user = instance.user
            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()

        # Update UserProfile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
