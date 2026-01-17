from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsStudent, IsSchoolAdminOrHigher
from apps.students.models import Grade, StudentGPA
from apps.students.serializers import GradeSerializer, StudentGPASerializer, StudentPortalSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class GradeViewSet(viewsets.ModelViewSet):
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return Grade.objects.all()
        elif self.request.user.role == 'student':
            return Grade.objects.filter(student=self.request.user)
        return Grade.objects.filter(student__school=self.request.user.school)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSchoolAdminOrHigher()]
        return [IsAuthenticated()]


class StudentPortalViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsStudent]
    
    @action(detail=False, methods=['get'])
    def my_portal(self, request):
        """Get student portal data"""
        serializer = StudentPortalSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def attendance_report(self, request):
        """Get student attendance report"""
        from apps.attendance.models import Attendance
        
        attendances = Attendance.objects.filter(student=request.user)
        total = attendances.count()
        present = attendances.filter(status='present').count()
        percentage = (present / total * 100) if total > 0 else 0
        
        return Response({
            'total_classes': total,
            'present': present,
            'absent': attendances.filter(status='absent').count(),
            'late': attendances.filter(status='late').count(),
            'percentage': percentage,
        })
    
    @action(detail=False, methods=['get'])
    def exam_results(self, request):
        """Get exam results"""
        grades = Grade.objects.filter(student=request.user, assessment_type='exam')
        return Response(GradeSerializer(grades, many=True).data)
    
    @action(detail=False, methods=['get'])
    def assignments(self, request):
        """Get all assignments for enrolled classes"""
        from apps.academics.models import Enrollment
        from apps.assignments.models import Assignment, AssignmentSubmission
        
        enrollments = Enrollment.objects.filter(student=request.user, is_active=True)
        classes = [e.class_obj for e in enrollments]
        assignments = Assignment.objects.filter(class_obj__in=classes)
        
        assignment_data = []
        for assignment in assignments:
            submission = AssignmentSubmission.objects.filter(
                assignment=assignment,
                student=request.user
            ).first()
            
            assignment_data.append({
                'assignment': {
                    'id': assignment.id,
                    'title': assignment.title,
                    'description': assignment.description,
                    'due_date': assignment.due_date,
                },
                'submission': {
                    'status': submission.status if submission else 'not_submitted',
                    'score': submission.score if submission else None,
                    'feedback': submission.feedback if submission else None,
                } if submission else None
            })
        
        return Response(assignment_data)
