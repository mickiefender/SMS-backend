from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.users.models import User, TeacherProfile, StudentProfile


class UserSerializer(serializers.ModelSerializer):
    school_id = serializers.IntegerField(source='school.id', read_only=True, allow_null=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'username', 'phone', 'role', 'school', 'school_id', 'is_active_user', 'created_at']
        read_only_fields = ['id', 'created_at', 'school_id']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password2', 'phone', 'role', 'school']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class TeacherProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_data = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TeacherProfile
        fields = ['id', 'user', 'user_data', 'user_email', 'user_name', 'first_name', 'last_name', 'email', 'username', 'employee_id', 'qualification', 'experience_years', 'department', 'bio', 'created_at']
        read_only_fields = ['id', 'created_at', 'user_email', 'user_name', 'first_name', 'last_name', 'email', 'username', 'user_data']
    
    def get_user_data(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
                'username': obj.user.username,
                'phone': obj.user.phone,
                'role': obj.user.role,
            }
        return None
    
    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return None


class StudentProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_data = serializers.SerializerMethodField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'user_data', 'user_email', 'user_name', 'first_name', 'last_name', 'email', 'username', 'student_id', 'level', 'department', 'enrollment_date', 'created_at']
        read_only_fields = ['id', 'enrollment_date', 'created_at', 'user_email', 'user_name', 'first_name', 'last_name', 'email', 'username', 'user_data']
    
    def get_user_data(self, obj):
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email,
                'first_name': obj.user.first_name,
                'last_name': obj.user.last_name,
                'username': obj.user.username,
                'phone': obj.user.phone,
                'role': obj.user.role,
            }
        return None
    
    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return None
