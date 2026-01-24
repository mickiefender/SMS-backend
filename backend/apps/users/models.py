from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.schools.models import School


class User(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', 'Super Admin'),
        ('school_admin', 'School Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    )
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True)
    is_active_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', 'role']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} - {self.role}"


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    qualification = models.CharField(max_length=255, blank=True)
    experience_years = models.IntegerField(default=0)
    department = models.ForeignKey('academics.Department', on_delete=models.SET_NULL, null=True, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Teacher Profiles"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Teacher"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=50, unique=True)
    level = models.ForeignKey('academics.Level', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey('academics.Department', on_delete=models.SET_NULL, null=True, blank=True)
    enrollment_date = models.DateField(auto_now_add=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Student Profiles"
    
    def save(self, *args, **kwargs):
        # Auto-generate student_id if not provided
        if not self.student_id:
            from datetime import datetime
            
            # Get school initials
            school_name = self.user.school.name if self.user.school else "STU"
            words = school_name.split()
            school_initials = ''.join([word[0].upper() for word in words if word])[:3]
            
            year = datetime.now().year
            
            # Get the count of students in this school for this year
            count = StudentProfile.objects.filter(
                user__school=self.user.school,
                created_at__year=year
            ).count() + 1
            
            self.student_id = f"{school_initials}{year}{count:05d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Student ({self.student_id})"
