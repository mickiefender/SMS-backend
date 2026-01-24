from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsSchoolAdminOrHigher, IsSchoolAdminOrTeacher
from apps.academics.models import (
    Faculty, Department, Level, Subject, Class,
    ClassSubject, Enrollment, Timetable, AcademicCalendarEvent,
    Exam, ExamResult, SchoolFees, SchoolEvent, Document, Notice, UserProfilePicture,
    ClassTeacher, StudentClass, ClassSubjectTeacher, Syllabus, SyllabusTopic
)
from apps.academics.serializers import (
    FacultySerializer, DepartmentSerializer, LevelSerializer,
    SubjectSerializer, ClassSerializer, ClassSubjectSerializer,
    EnrollmentSerializer, TimetableSerializer, AcademicCalendarEventSerializer,
    ExamSerializer, ExamResultSerializer, SchoolFeesSerializer,
    SchoolEventSerializer, DocumentSerializer, NoticeSerializer, UserProfilePictureSerializer,
    ClassTeacherSerializer, StudentClassSerializer, ClassSubjectTeacherSerializer,
    SyllabusSerializer, SyllabusTopicSerializer
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


class SyllabusViewSet(viewsets.ModelViewSet):
    serializer_class = SyllabusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        if school_id is None:
            return Syllabus.objects.all()
        return Syllabus.objects.filter(subject__school_id=school_id)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrTeacher()]
        return [IsAuthenticated()]


class SyllabusTopicViewSet(viewsets.ModelViewSet):
    serializer_class = SyllabusTopicSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        if school_id is None:
            return SyllabusTopic.objects.all()
        return SyllabusTopic.objects.filter(syllabus__subject__school_id=school_id)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrTeacher()]
        return [IsAuthenticated()]


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
        
        # Students see only classes they're enrolled in
        if self.request.user.role == 'student':
            student_class_ids = StudentClass.objects.filter(student=self.request.user, is_active=True).values_list('class_obj_id', flat=True)
            if school_id:
                return Class.objects.filter(id__in=student_class_ids, school_id=school_id)
            return Class.objects.filter(id__in=student_class_ids)
        
        # Teachers see classes they manage or teach
        if self.request.user.role == 'teacher':
            teacher_class_ids = ClassTeacher.objects.filter(teacher=self.request.user).values_list('class_obj_id', flat=True)
            if school_id:
                return Class.objects.filter(id__in=teacher_class_ids, school_id=school_id)
            return Class.objects.filter(id__in=teacher_class_ids)
        
        # Admins and super_admins see all classes in their school
        if school_id is None:
            return Class.objects.all()
        return Class.objects.filter(school_id=school_id)
    
    def create(self, request, *args, **kwargs):
        try:
            print(f"[v0] ClassViewSet.create - received data: {request.data}")
            return super().create(request, *args, **kwargs)
        except Exception as e:
            print(f"[v0] ClassViewSet.create - error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        try:
            if self.request.user.school_id:
                print(f"[v0] ClassViewSet.perform_create - saving class with school_id: {self.request.user.school_id}")
                print(f"[v0] ClassViewSet.perform_create - validated data: {serializer.validated_data}")
                serializer.save(school_id=self.request.user.school_id)
            else:
                print(f"[v0] ClassViewSet.perform_create - no school_id for user: {self.request.user}")
                serializer.save()
            print(f"[v0] ClassViewSet.perform_create - class saved successfully: {serializer.data}")
        except Exception as e:
            print(f"[v0] ClassViewSet.perform_create - error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrHigher()]
        return [IsAuthenticated()]


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
        
        # Students can only see their own enrollments
        if self.request.user.role == 'student':
            if school_id:
                return Enrollment.objects.filter(student=self.request.user, class_obj__school_id=school_id)
            return Enrollment.objects.filter(student=self.request.user)
        
        # Teachers can see enrollments for their classes
        if self.request.user.role == 'teacher':
            if school_id:
                return Enrollment.objects.filter(class_obj__teachers__teacher=self.request.user, class_obj__school_id=school_id).distinct()
            return Enrollment.objects.filter(class_obj__teachers__teacher=self.request.user).distinct()
        
        # Admins see all
        if school_id:
            return Enrollment.objects.filter(class_obj__school_id=school_id)
        return Enrollment.objects.all()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrTeacher()]
        return [IsAuthenticated()]


class TimetableViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        
        # Students see timetables for their assigned classes
        if self.request.user.role == 'student':
            student_classes = StudentClass.objects.filter(student=self.request.user, is_active=True).values_list('class_obj_id', flat=True)
            if school_id:
                return Timetable.objects.filter(class_obj_id__in=student_classes, class_obj__school_id=school_id)
            return Timetable.objects.filter(class_obj_id__in=student_classes)
        
        # Teachers see timetables for classes they teach
        if self.request.user.role == 'teacher':
            if school_id:
                return Timetable.objects.filter(teacher=self.request.user, class_obj__school_id=school_id)
            return Timetable.objects.filter(teacher=self.request.user)
        
        # Admins see all
        if school_id:
            return Timetable.objects.filter(class_obj__school_id=school_id)
        return Timetable.objects.all()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrTeacher()]
        return [IsAuthenticated()]


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


class ClassTeacherViewSet(viewsets.ModelViewSet):
    serializer_class = ClassTeacherSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        if school_id is None:
            return ClassTeacher.objects.all()
        return ClassTeacher.objects.filter(class_obj__school_id=school_id)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrHigher()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        try:
            print(f"[v0] ClassTeacherViewSet.create - data: {request.data}")
            return super().create(request, *args, **kwargs)
        except Exception as e:
            print(f"[v0] ClassTeacherViewSet.create - error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def perform_create(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            print(f"[v0] ClassTeacherViewSet.perform_create - error: {str(e)}")
            raise


class StudentClassViewSet(viewsets.ModelViewSet):
    serializer_class = StudentClassSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        
        # Students can only see their own class assignments
        if self.request.user.role == 'student':
            if school_id:
                return StudentClass.objects.filter(student=self.request.user, class_obj__school_id=school_id)
            return StudentClass.objects.filter(student=self.request.user)
        
        # Teachers can see classes they manage
        if self.request.user.role == 'teacher':
            if school_id:
                return StudentClass.objects.filter(class_obj__teachers__teacher=self.request.user, class_obj__school_id=school_id)
            return StudentClass.objects.filter(class_obj__teachers__teacher=self.request.user)
        
        # Admins see all
        if school_id:
            return StudentClass.objects.filter(class_obj__school_id=school_id)
        return StudentClass.objects.all()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrHigher()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        try:
            print(f"[v0] StudentClassViewSet.create - data: {request.data}")
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            if 'student' in e.detail and any('does_not_exist' in code for code in e.get_codes()['student']):
                student_id = request.data.get('student')
                e.detail['student'] = [f"Student with id {student_id} does not exist."]
            raise e
        except Exception as e:
            print(f"[v0] StudentClassViewSet.create - error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def perform_create(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            print(f"[v0] StudentClassViewSet.perform_create - error: {str(e)}")
            raise


class ClassSubjectTeacherViewSet(viewsets.ModelViewSet):
    serializer_class = ClassSubjectTeacherSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        school_id = get_school_filter(self.request.user)
        
        # Teachers can see their own subject assignments
        if self.request.user.role == 'teacher':
            if school_id:
                return ClassSubjectTeacher.objects.filter(teacher=self.request.user, class_obj__school_id=school_id)
            return ClassSubjectTeacher.objects.filter(teacher=self.request.user)
        
        if school_id:
            return ClassSubjectTeacher.objects.filter(class_obj__school_id=school_id)
        return ClassSubjectTeacher.objects.all()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrHigher()]
        return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        try:
            print(f"[v0] ClassSubjectTeacherViewSet.create - data: {request.data}")
            return super().create(request, *args, **kwargs)
        except Exception as e:
            print(f"[v0] ClassSubjectTeacherViewSet.create - error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def perform_create(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            print(f"[v0] ClassSubjectTeacherViewSet.perform_create - error: {str(e)}")
            raise
