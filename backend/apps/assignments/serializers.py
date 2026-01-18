from rest_framework import serializers
from apps.assignments.models import Assignment, AssignmentSubmission
from apps.users.models import User
from apps.academics.models import Class, Subject


class AssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    
    class_obj = serializers.PrimaryKeyRelatedField(queryset=Class.objects.all())
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='teacher'), required=False)
    
    class Meta:
        model = Assignment
        fields = ['id', 'class_obj', 'subject', 'teacher', 'teacher_name', 'title', 'description', 'file', 'due_date', 'created_at', 'updated_at']
        read_only_fields = ['teacher_name', 'created_at', 'updated_at']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    
    class Meta:
        model = AssignmentSubmission
        fields = '__all__'
