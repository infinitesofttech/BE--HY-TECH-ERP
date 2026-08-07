from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db import transaction
from .models import User, ContactInfo, Feedback, Role, LoginLog, UserActivityLog
from apps.contacts.models import Company


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid email or password.')
        user = authenticate(username=user_obj.username, password=password)
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('Account is disabled.')
        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    manager_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True, default='')
    designation_name = serializers.CharField(source='designation.name', read_only=True, default='')

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'username', 'role',
            'phone', 'avatar', 'territory', 'pin_code', 'manager', 'manager_name',
            'device_token', 'address', 'city', 'state', 'date_of_birth',
            'joining_date', 'department', 'department_name', 'designation',
            'designation_name', 'shift_start_time', 'shift_end_time', 'salary',
            'is_active', 'date_joined',
        ]
        read_only_fields = ['id', 'date_joined', 'is_active']
        extra_kwargs = {
            'device_token': {'write_only': True},
        }

    def get_manager_name(self, obj):
        if obj.manager is None:
            return ''
        return obj.manager.get_full_name() or obj.manager.email


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'role',
            'phone', 'territory', 'pin_code', 'manager', 'address', 'city',
            'state', 'date_of_birth', 'joining_date', 'department',
            'designation', 'shift_start_time', 'shift_end_time', 'salary', 'password',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CompanyRegisterSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='name', max_length=200)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Company
        fields = [
            'company_name', 'email', 'password', 'confirm_password',
            'email_opt_out', 'phone', 'phone_2', 'fax', 'website', 'reviews',
            'avatar', 'industry', 'tags', 'source', 'language', 'description',
            'visibility', 'street_address', 'city', 'state', 'country',
            'zipcode', 'facebook', 'skype', 'linkedin', 'twitter', 'whatsapp',
            'instagram', 'status',
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError(
                {'confirm_password': 'Passwords do not match.'},
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        company_name = validated_data['name']
        email = validated_data['email']

        user = User(
            email=email,
            username=email,
            first_name=company_name,
            role='company',
        )
        user.set_password(password)
        user.save()

        return Company.objects.create(owner=user, **validated_data)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'avatar', 'address', 'city', 'state']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class DeleteAccountRequestSerializer(serializers.Serializer):
    reason = serializers.CharField()


class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = ['id', 'phone', 'email', 'address', 'latitude', 'longitude', 'working_hours']


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'name', 'email', 'phone', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions', 'created_at']
        read_only_fields = ['id', 'created_at']


class LoginLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = LoginLog
        fields = [
            'id', 'user', 'user_name', 'login_time', 'logout_time',
            'session_duration', 'ip_address', 'device', 'status',
        ]
        read_only_fields = ['id', 'login_time']

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return None


class UserActivityLogSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = UserActivityLog
        fields = [
            'id', 'user', 'user_name', 'action', 'module',
            'record_id', 'ip_address', 'action_date',
        ]
        read_only_fields = ['id', 'user', 'action_date']

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return None
