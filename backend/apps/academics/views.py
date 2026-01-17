from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsSchoolAdminOrHigher
from apps.academics.models import (
    Faculty, Department, Level, Subject, Class,
    ClassSubject, Enrollment, Timetable, AcademicCalendarEvent
)
from apps.academics.serializers import (
    FacultySerializer, DepartmentSerializer, LevelSerializer,
    SubjectSerializer, ClassSerializer, ClassSubjectSerializer,
    EnrollmentSerializer, TimetableSerializer, AcademicCalendarEventSerializer
)


class FacultyViewSet(viewsets.ModelViewSet):
    serializer_class = FacultySerializer
    permission_classes = [IsAuthenticated, IsSchoolAdminOrHigher]
    
    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return Faculty.objects.all()
        return Faculty.objects.filter(school=self.request.user.school)


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdminOrHigher]
    
    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return Department.objects.all()
        return Department.objects.filter(faculty__school=self.request.user.school)


class LevelViewSet(viewsets.ModelViewSet):
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdminOrHigher]
    
    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return Level.objects.all()
        return Level.objects.filter(school=self.request.user.school)


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdminOrHigher]
    
    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return Subject.objects.all()
        return Subject.objects.filter(school=self.request.user.school)


class ClassViewSet(viewsets.ModelViewSet):
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return Class.objects.all()
        return Class.objects.filter(school=self.request.user.school)


class ClassSubjectViewSet(viewsets.ModelViewSet):
    serializer_class = ClassSubjectSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdminOrHigher]
    
    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return ClassSubject.objects.all()
        return ClassSubject.objects.filter(class_obj__school=self.request.user.school)


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return Enrollment.objects.all()
        return Enrollment.objects.filter(class_obj__school=self.request.user.school)


class TimetableViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return Timetable.objects.all()
        return Timetable.objects.filter(class_obj__school=self.request.user.school)


class AcademicCalendarEventViewSet(viewsets.ModelViewSet):
    serializer_class = AcademicCalendarEventSerializer
    permission_classes = [IsAuthenticated, IsSchoolAdminOrHigher]
    
    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return AcademicCalendarEvent.objects.all()
        return AcademicCalendarEvent.objects.filter(school=self.request.user.school)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, school=self.request.user.school)
