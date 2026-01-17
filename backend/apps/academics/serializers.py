from rest_framework import serializers
from apps.academics.models import (
    Faculty, Department, Level, Subject, Class,
    ClassSubject, Enrollment, Timetable, AcademicCalendarEvent
)


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    faculty_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = '__all__'
    
    def get_faculty_name(self, obj):
        return obj.faculty.name if obj.faculty else None


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class ClassSerializer(serializers.ModelSerializer):
    level_name = serializers.SerializerMethodField()
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = '__all__'
    
    def get_level_name(self, obj):
        return obj.level.name if obj.level else None
    
    def get_student_count(self, obj):
        return obj.enrollments.filter(is_active=True).values('student').distinct().count()


class ClassSubjectSerializer(serializers.ModelSerializer):
    class_obj = serializers.PrimaryKeyRelatedField(queryset=Class.objects.all())
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    
    subject_name = serializers.SerializerMethodField()
    subject_code = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ClassSubject
        fields = ['id', 'class_obj', 'subject', 'teacher', 'subject_name', 'subject_code', 'class_name', 'teacher_name', 'created_at']
    
    def get_subject_name(self, obj):
        return obj.subject.name if obj.subject else None
    
    def get_subject_code(self, obj):
        return obj.subject.code if obj.subject else None
    
    def get_class_name(self, obj):
        return obj.class_obj.name if obj.class_obj else None
    
    def get_teacher_name(self, obj):
        if obj.teacher:
            return obj.teacher.get_full_name() or obj.teacher.username
        return None


class EnrollmentSerializer(serializers.ModelSerializer):
    class_obj = serializers.PrimaryKeyRelatedField(queryset=Class.objects.all())
    
    student_name = serializers.SerializerMethodField()
    student_email = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Enrollment
        fields = ['id', 'class_obj', 'student', 'subject', 'enrollment_date', 'is_active', 'student_name', 'student_email', 'class_name', 'subject_name']
    
    def get_student_name(self, obj):
        if obj.student:
            return obj.student.get_full_name() or obj.student.username
        return None
    
    def get_student_email(self, obj):
        return obj.student.email if obj.student else None
    
    def get_class_name(self, obj):
        return obj.class_obj.name if obj.class_obj else None
    
    def get_subject_name(self, obj):
        return obj.subject.name if obj.subject else None


class TimetableSerializer(serializers.ModelSerializer):
    class_obj = serializers.PrimaryKeyRelatedField(queryset=Class.objects.all())
    
    subject_name = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Timetable
        fields = ['id', 'class_obj', 'subject', 'teacher', 'day', 'start_time', 'end_time', 'venue', 'subject_name', 'class_name', 'teacher_name', 'created_at', 'updated_at']
    
    def get_subject_name(self, obj):
        return obj.subject.name if obj.subject else None
    
    def get_class_name(self, obj):
        return obj.class_obj.name if obj.class_obj else None
    
    def get_teacher_name(self, obj):
        if obj.teacher:
            return obj.teacher.get_full_name() or obj.teacher.username
        return None


class AcademicCalendarEventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AcademicCalendarEvent
        fields = '__all__'
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None
