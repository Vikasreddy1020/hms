"""Serializers for accounts app."""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Doctor, Patient

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role',
                  'phone', 'address', 'date_of_birth', 'profile_picture',
                  'is_verified', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_verified', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name',
                  'last_name', 'role', 'phone', 'address', 'date_of_birth']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value


class DoctorSerializer(serializers.ModelSerializer):
    """Serializer for Doctor model."""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'user_id', 'full_name', 'email', 'specialization',
                  'qualification', 'experience_years', 'license_number',
                  'consultation_fee', 'bio', 'is_available', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DoctorCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating doctors."""
    user = UserCreateSerializer()

    class Meta:
        model = Doctor
        fields = ['user', 'specialization', 'qualification', 'experience_years',
                  'license_number', 'consultation_fee', 'bio', 'is_available']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = 'doctor'
        password = user_data.pop('password')
        password_confirm = user_data.pop('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        
        user = User.objects.create_user(password=password, **user_data)
        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model."""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'user', 'user_id', 'full_name', 'email', 'blood_group',
                  'gender', 'emergency_contact', 'emergency_contact_name',
                  'medical_history', 'allergies', 'insurance_number',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PatientCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating patients."""
    user = UserCreateSerializer()

    class Meta:
        model = Patient
        fields = ['user', 'blood_group', 'gender', 'emergency_contact',
                  'emergency_contact_name', 'medical_history', 'allergies', 'insurance_number']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = 'patient'
        password = user_data.pop('password')
        password_confirm = user_data.pop('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        
        user = User.objects.create_user(password=password, **user_data)
        patient = Patient.objects.create(user=user, **validated_data)
        return patient


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
