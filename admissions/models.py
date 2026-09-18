from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    total_seats = models.IntegerField()
    fees = models.DecimalField(max_digits=10, decimal_places=2)
    cutoff_marks = models.DecimalField(max_digits=5, decimal_places=2, help_text="Percentage required")

    def __str__(self):
        return f"{self.name} ({self.code})"

class ApplicationForm(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Documents Verified', 'Documents Verified'),
        ('Merit Approved', 'Merit Approved'),
        ('Rejected', 'Rejected'),
        ('Paid', 'Paid'),
        ('Admitted', 'Admitted'),
    )
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    dob = models.DateField(verbose_name="Date of Birth")
    address = models.TextField()
    marks_10th = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="10th Percentage")
    marks_12th = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="12th Percentage")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application: {self.full_name} for {self.course.name if self.course else 'N/A'}"

class Document(models.Model):
    application = models.OneToOneField(ApplicationForm, on_delete=models.CASCADE, related_name='document')
    photo = models.ImageField(upload_to='applicant_photos/')
    signature = models.ImageField(upload_to='signatures/')
    marksheet_10th = models.FileField(upload_to='marksheets/')
    marksheet_12th = models.FileField(upload_to='marksheets/')
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Documents for {self.application.full_name}"

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )
    application = models.OneToOneField(ApplicationForm, on_delete=models.CASCADE, related_name='payment')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    paid_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"
