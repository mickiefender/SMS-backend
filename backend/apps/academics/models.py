from django.db import models
from apps.schools.models import School


class Faculty(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='faculties')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'name']
        verbose_name_plural = "Faculties"
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"


class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['faculty', 'name']
    
    def __str__(self):
        return f"{self.faculty.name} - {self.name}"


class Level(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='levels')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'name']
        ordering = ['order']
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"


class Subject(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='subjects')
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    credit_hours = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Class(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=100)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True)
    capacity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'name', 'level']
        verbose_name_plural = "Classes"
    
    def __str__(self):
        return f"{self.school.name} - {self.name}"


class ClassSubject(models.Model):
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'teacher'})
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['class_obj', 'subject']
    
    def __str__(self):
        return f"{self.class_obj.name} - {self.subject.code}"


class Enrollment(models.Model):
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey('users.User', on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='enrollments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['class_obj', 'student', 'subject']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.class_obj.name}"


class Timetable(models.Model):
    DAY_CHOICES = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )
    
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='timetables')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'teacher'})
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['class_obj', 'subject', 'day', 'start_time']
        verbose_name_plural = "Timetables"
    
    def __str__(self):
        return f"{self.class_obj.name} - {self.subject.code} - {self.day}"

class AcademicCalendarEvent(models.Model):
    EVENT_TYPE_CHOICES = (
        ('holiday', 'Holiday'),
        ('exam', 'Exam'),
        ('event', 'Event'),
        ('break', 'Break'),
    )
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='calendar_events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'title', 'start_date']
        ordering = ['start_date']
    
    def __str__(self):
        return f"{self.school.name} - {self.title}"


class Exam(models.Model):
    """Upcoming exams for students"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exams')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='exams')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    exam_date = models.DateField()
    exam_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    venue = models.CharField(max_length=255, blank=True)
    total_marks = models.IntegerField(default=100)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'teacher'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['school', 'subject', 'class_obj', 'exam_date']
        ordering = ['exam_date']
    
    def __str__(self):
        return f"{self.subject.name} - {self.exam_date}"


class ExamResult(models.Model):
    """Student exam results"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='exam_results')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey('users.User', on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='exam_results')
    marks_obtained = models.FloatField()
    percentage = models.FloatField(default=0, editable=False)
    grade = models.CharField(max_length=5, blank=True)
    remarks = models.TextField(blank=True)
    recorded_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='recorded_exam_results', limit_choices_to={'role': 'teacher'})
    recorded_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['exam', 'student']
        ordering = ['-recorded_date']
    
    def save(self, *args, **kwargs):
        if self.exam.total_marks > 0:
            self.percentage = (self.marks_obtained / self.exam.total_marks) * 100
            self.grade = self.calculate_grade()
        super().save(*args, **kwargs)
    
    def calculate_grade(self):
        if self.percentage >= 90:
            return 'A'
        elif self.percentage >= 80:
            return 'B'
        elif self.percentage >= 70:
            return 'C'
        elif self.percentage >= 60:
            return 'D'
        else:
            return 'F'
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.exam.subject.name}"


class SchoolFees(models.Model):
    """Student school fees"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    )
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='fees')
    student = models.ForeignKey('users.User', on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='school_fees')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='fees')
    title = models.CharField(max_length=255)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.title}"


class SchoolEvent(models.Model):
    """School events/activities"""
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='school_events')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_date = models.DateField()
    event_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-event_date']
    
    def __str__(self):
        return f"{self.title} - {self.event_date}"


class Document(models.Model):
    """School documents for students/teachers"""
    DOCUMENT_TYPE_CHOICES = (
        ('certificate', 'Certificate'),
        ('transcript', 'Transcript'),
        ('syllabus', 'Syllabus'),
        ('assignment', 'Assignment'),
        ('notes', 'Notes'),
        ('other', 'Other'),
    )
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='documents/')
    related_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True)
    related_subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title}"


class Notice(models.Model):
    """Notice board for school announcements"""
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='notices')
    title = models.CharField(max_length=255)
    content = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    posted_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['school', 'is_active']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.school.name} - {self.title}"


class UserProfilePicture(models.Model):
    """Profile pictures for students and teachers"""
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='profile_picture')
    picture = models.ImageField(upload_to='profile_pictures/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "User Profile Pictures"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - Profile Picture"
