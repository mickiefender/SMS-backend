from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.academics.views import (
    FacultyViewSet, DepartmentViewSet, LevelViewSet, SubjectViewSet,
    ClassViewSet, ClassSubjectViewSet, EnrollmentViewSet, TimetableViewSet,
    AcademicCalendarEventViewSet
)

router = DefaultRouter()
router.register(r'faculties', FacultyViewSet, basename='faculty')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'levels', LevelViewSet, basename='level')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'classes', ClassViewSet, basename='class')
router.register(r'class-subjects', ClassSubjectViewSet, basename='class-subject')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'timetables', TimetableViewSet, basename='timetable')
router.register(r'calendar-events', AcademicCalendarEventViewSet, basename='calendar-event')

urlpatterns = [
    path('', include(router.urls)),
]
