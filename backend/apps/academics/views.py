from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsSchoolAdminOrHigher, IsSchoolAdminOrTeacher
from apps.academics.models import (
    Faculty, Department, Level, Subject, Class,
    ClassSubject, Enrollment, Timetable, AcademicCalendarEvent,
    Exam, ExamResult, SchoolFees, SchoolEvent, Document, Notice, UserProfilePicture
)
from apps.academics.serializers import (
    FacultySerializer, DepartmentSerializer, LevelSerializer,
    SubjectSerializer, ClassSerializer, ClassSubjectSerializer,
    EnrollmentSerializer, TimetableSerializer, AcademicCalendarEventSerializer,
    ExamSerializer, ExamResultSerializer, SchoolFeesSerializer,
    SchoolEventSerializer, DocumentSerializer, NoticeSerializer, UserProfilePictureSerializer
)


def get_school_filter(user):
    """Get school for filtering, returns None for super_admin or if no school assigned"""
    try:
        if user.role == 'super_admin':
            return None
        # Check if school_id exists and is not None
        if hasattr(user, 'school_id') and user.school_id:
            return user.school_id
        return None
    except Exception as e:
        print(f"[v0] Error in get_school_filter: {e}")
        return None


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


class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = ExamSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrTeacher()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        try:
            school_id = get_school_filter(self.request.user)
            if school_id:
                return Exam.objects.filter(school_id=school_id).order_by('exam_date')
            return Exam.objects.all().order_by('exam_date')
        except Exception as e:
            print(f"[v0] Error in ExamViewSet.get_queryset: {e}")
            return Exam.objects.all().order_by('exam_date')
    
    def perform_create(self, serializer):
        school_id = getattr(self.request.user, 'school_id', None)
        if school_id:
            serializer.save(created_by=self.request.user, school_id=school_id)
        else:
            serializer.save(created_by=self.request.user)


class ExamResultViewSet(viewsets.ModelViewSet):
    serializer_class = ExamResultSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrTeacher()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        try:
            school_id = get_school_filter(self.request.user)
            if school_id:
                return ExamResult.objects.filter(school_id=school_id).order_by('-recorded_date')
            return ExamResult.objects.all().order_by('-recorded_date')
        except Exception as e:
            print(f"[v0] Error in ExamResultViewSet.get_queryset: {e}")
            return ExamResult.objects.all().order_by('-recorded_date')
    
    def perform_create(self, serializer):
        school_id = getattr(self.request.user, 'school_id', None)
        if school_id:
            serializer.save(recorded_by=self.request.user, school_id=school_id)
        else:
            serializer.save(recorded_by=self.request.user)


class SchoolFeesViewSet(viewsets.ModelViewSet):
    serializer_class = SchoolFeesSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            school_id = get_school_filter(self.request.user)
            
            # Students can only see their own fees
            if self.request.user.role == 'student':
                if school_id:
                    return SchoolFees.objects.filter(student=self.request.user, school_id=school_id).order_by('-due_date')
                return SchoolFees.objects.filter(student=self.request.user).order_by('-due_date')
            
            if school_id:
                return SchoolFees.objects.filter(school_id=school_id).order_by('-due_date')
            return SchoolFees.objects.all().order_by('-due_date')
        except Exception as e:
            print(f"[v0] Error in SchoolFeesViewSet.get_queryset: {e}")
            if self.request.user.role == 'student':
                return SchoolFees.objects.filter(student=self.request.user).order_by('-due_date')
            return SchoolFees.objects.all().order_by('-due_date')
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrHigher()]
        return [IsAuthenticated()]


class SchoolEventViewSet(viewsets.ModelViewSet):
    serializer_class = SchoolEventSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrHigher()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        try:
            school_id = get_school_filter(self.request.user)
            if school_id:
                return SchoolEvent.objects.filter(school_id=school_id).order_by('-event_date')
            return SchoolEvent.objects.all().order_by('-event_date')
        except Exception as e:
            print(f"[v0] Error in SchoolEventViewSet.get_queryset: {e}")
            return SchoolEvent.objects.all().order_by('-event_date')
    
    def perform_create(self, serializer):
        school_id = getattr(self.request.user, 'school_id', None)
        if school_id:
            serializer.save(created_by=self.request.user, school_id=school_id)
        else:
            serializer.save(created_by=self.request.user)


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrTeacher()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        try:
            school_id = get_school_filter(self.request.user)
            if school_id:
                return Document.objects.filter(school_id=school_id).order_by('-created_at')
            return Document.objects.all().order_by('-created_at')
        except Exception as e:
            print(f"[v0] Error in DocumentViewSet.get_queryset: {e}")
            return Document.objects.all().order_by('-created_at')
    
    def perform_create(self, serializer):
        school_id = getattr(self.request.user, 'school_id', None)
        if school_id:
            serializer.save(uploaded_by=self.request.user, school_id=school_id)
        else:
            serializer.save(uploaded_by=self.request.user)


class NoticeViewSet(viewsets.ModelViewSet):
    serializer_class = NoticeSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrHigher()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        try:
            school_id = get_school_filter(self.request.user)
            if school_id:
                return Notice.objects.filter(school_id=school_id, is_active=True).order_by('-created_at')
            return Notice.objects.filter(is_active=True).order_by('-created_at')
        except Exception as e:
            print(f"[v0] Error in NoticeViewSet.get_queryset: {e}")
            return Notice.objects.filter(is_active=True).order_by('-created_at')
    
    def perform_create(self, serializer):
        school_id = getattr(self.request.user, 'school_id', None)
        if school_id:
            serializer.save(posted_by=self.request.user, school_id=school_id)
        else:
            serializer.save(posted_by=self.request.user)


class UserProfilePictureViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfilePictureSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        if school_id is None:
            return UserProfilePicture.objects.all()
        return UserProfilePicture.objects.filter(user__school_id=school_id)
    
    def perform_create(self, serializer):
        # Users can only upload their own profile pictures, admins can upload for others
        if self.request.user.role == 'school_admin':
            serializer.save()
        else:
            serializer.save(user=self.request.user)
