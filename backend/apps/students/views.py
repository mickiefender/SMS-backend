from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsStudent, IsSchoolAdminOrHigher, IsSchoolAdminOrTeacher
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
            return [IsAuthenticated(), IsSchoolAdminOrTeacher()]
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
        try:
            from apps.academics.models import Enrollment
            from apps.assignments.models import Assignment, AssignmentSubmission
            
            print(f"[v0] Fetching assignments for user: {request.user}")
            
            # Get enrollments for student
            enrollments = Enrollment.objects.filter(student=request.user, is_active=True)
            print(f"[v0] Found {enrollments.count()} enrollments")
            
            classes = [e.class_obj for e in enrollments]
            if not classes:
                print("[v0] No classes found for student")
                return Response([])
            
            # Get assignments for those classes
            assignments = Assignment.objects.filter(class_obj__in=classes)
            print(f"[v0] Found {assignments.count()} assignments")
            
            assignment_data = []
            for assignment in assignments:
                try:
                    submission = AssignmentSubmission.objects.filter(
                        assignment=assignment,
                        student=request.user
                    ).first()
                    
                    assignment_data.append({
                        'assignment': {
                            'id': assignment.id,
                            'title': assignment.title,
                            'description': assignment.description,
                            'due_date': str(assignment.due_date) if assignment.due_date else None,
                        },
                        'submission': {
                            'status': submission.status if submission else 'not_submitted',
                            'score': submission.score if submission else None,
                            'feedback': submission.feedback if submission else None,
                        } if submission else None
                    })
                except Exception as e:
                    print(f"[v0] Error processing assignment {assignment.id}: {e}")
                    continue
            
            print(f"[v0] Returning {len(assignment_data)} assignments")
            return Response(assignment_data)
        
        except Exception as e:
            print(f"[v0] Error fetching assignments: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': str(e)}, status=400)
