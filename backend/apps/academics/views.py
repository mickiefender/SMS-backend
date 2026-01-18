from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsSchoolAdminOrHigher, IsSchoolAdminOrTeacher
from apps.academics.models import (
    Faculty, Department, Level, Subject, Class,
    ClassSubject, Enrollment, Timetable, AcademicCalendarEvent
)
from apps.academics.serializers import (
    FacultySerializer, DepartmentSerializer, LevelSerializer,
    SubjectSerializer, ClassSerializer, ClassSubjectSerializer,
    EnrollmentSerializer, TimetableSerializer, AcademicCalendarEventSerializer
)


def get_school_filter(user):
    """Get school for filtering, returns None for super_admin or if no school assigned"""
    if user.role == 'super_admin':
        return None
    return user.school_id  # Use school_id instead of school to avoid extra query


class FacultyViewSet(viewsets.ModelViewSet):
    serializer_class = FacultySerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrHigher()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        if school_id is None:
            return Faculty.objects.all()
        return Faculty.objects.filter(school_id=school_id)


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrHigher()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        if school_id is None:
            return Department.objects.all()
        return Department.objects.filter(faculty__school_id=school_id)


class LevelViewSet(viewsets.ModelViewSet):
    serializer_class = LevelSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrHigher()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        if school_id is None:
            return Level.objects.all()
        return Level.objects.filter(school_id=school_id)


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrHigher()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        if school_id is None:
            return Subject.objects.all()
        return Subject.objects.filter(school_id=school_id)


class ClassViewSet(viewsets.ModelViewSet):
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        if school_id is None:
            return Class.objects.all()
        return Class.objects.filter(school_id=school_id)
    
    def perform_create(self, serializer):
        if self.request.user.school_id:
            serializer.save(school_id=self.request.user.school_id)
        else:
            serializer.save()


class ClassSubjectViewSet(viewsets.ModelViewSet):
    serializer_class = ClassSubjectSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrHigher()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        if school_id is None:
            return ClassSubject.objects.all()
        return ClassSubject.objects.filter(class_obj__school_id=school_id)


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        if school_id is None:
            return Enrollment.objects.all()
        return Enrollment.objects.filter(class_obj__school_id=school_id)


class TimetableViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        if school_id is None:
            return Timetable.objects.all()
        return Timetable.objects.filter(class_obj__school_id=school_id)


class AcademicCalendarEventViewSet(viewsets.ModelViewSet):
    serializer_class = AcademicCalendarEventSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrHigher()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        if school_id is None:
            return AcademicCalendarEvent.objects.all()
        return AcademicCalendarEvent.objects.filter(school_id=school_id)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, school_id=self.request.user.school_id)
