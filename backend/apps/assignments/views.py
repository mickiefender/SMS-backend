from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsTeacher
from apps.assignments.models import Assignment, AssignmentSubmission
from apps.assignments.serializers import AssignmentSerializer, AssignmentSubmissionSerializer


class AssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return Assignment.objects.all()
        elif self.request.user.role == 'teacher':
            return Assignment.objects.filter(teacher=self.request.user)
        return Assignment.objects.filter(class_obj__school=self.request.user.school)
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsTeacher()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)


class AssignmentSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = AssignmentSubmissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'super_admin':
            return AssignmentSubmission.objects.all()
        elif self.request.user.role == 'student':
            return AssignmentSubmission.objects.filter(student=self.request.user)
        return AssignmentSubmission.objects.filter(assignment__class_obj__school=self.request.user.school)
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """Submit an assignment"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(student=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTeacher])
    def grade(self, request, pk=None):
        """Grade a submission"""
        submission = self.get_object()
        submission.score = request.data.get('score')
        submission.feedback = request.data.get('feedback', '')
        submission.status = 'graded'
        submission.graded_at = timezone.now()
        submission.save()
        return Response(self.get_serializer(submission).data)
