from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.students.views import GradeViewSet, StudentPortalViewSet

router = DefaultRouter()
router.register(r'grades', GradeViewSet, basename='grade')
router.register(r'portal', StudentPortalViewSet, basename='student-portal')

urlpatterns = [
    path('', include(router.urls)),
]
