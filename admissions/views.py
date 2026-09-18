from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Count
from .models import UserProfile, Course, ApplicationForm, Document, Payment
from .forms import UserRegistrationForm, StudentApplicationForm, DocumentUploadForm, CourseForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Create UserProfile
            UserProfile.objects.create(
                user=user,
                role='student',
                phone_number=form.cleaned_data['phone_number']
            )
            messages.success(request, 'Registration successful. You can now login.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form, 'title': 'Student Registration'})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Check role and redirect
            if hasattr(user, 'userprofile') and user.userprofile.role == 'admin':
                return redirect('admin_dashboard')
            elif user.is_superuser:
                return redirect('admin_dashboard')
            else:
                return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'title': 'Login'})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def student_dashboard(request):
    try:
        application = ApplicationForm.objects.get(student=request.user)
        try:
            document = application.document
        except Document.DoesNotExist:
            document = None
        try:
            payment = application.payment
        except Payment.DoesNotExist:
            payment = None
    except ApplicationForm.DoesNotExist:
        application = None
        document = None
        payment = None

    context = {
        'application': application,
        'document': document,
        'payment': payment,
    }
    return render(request, 'student_dashboard.html', context)

@login_required
def apply(request):
    if ApplicationForm.objects.filter(student=request.user).exists():
        messages.warning(request, 'You have already submitted an application.')
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = StudentApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.student = request.user
            application.save()
            messages.success(request, 'Application submitted successfully. Please upload your documents.')
            return redirect('upload_documents')
    else:
        form = StudentApplicationForm()
    return render(request, 'apply.html', {'form': form})

@login_required
def upload_documents(request):
    application = get_object_or_404(ApplicationForm, student=request.user)
    if hasattr(application, 'document'):
        messages.warning(request, 'Documents already uploaded.')
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.application = application
            document.save()
            application.status = 'Documents Verified' # In reality, admin verifies this. Setting it for simplicity.
            application.save()
            messages.success(request, 'Documents uploaded successfully.')
            return redirect('student_dashboard')
    else:
        form = DocumentUploadForm()
    return render(request, 'upload_documents.html', {'form': form})

@login_required
def pay_fees(request):
    application = get_object_or_404(ApplicationForm, student=request.user)
    
    if application.status not in ['Merit Approved', 'Documents Verified']:
         messages.error(request, 'You are not eligible to pay fees yet.')
         return redirect('student_dashboard')

    if hasattr(application, 'payment') and application.payment.status == 'Completed':
        messages.info(request, 'Fees already paid.')
        return redirect('student_dashboard')

    if request.method == 'POST':
        # Simulate payment
        import uuid
        Payment.objects.create(
            application=application,
            transaction_id=str(uuid.uuid4()),
            amount=application.course.fees,
            status='Completed'
        )
        application.status = 'Paid'
        application.save()
        messages.success(request, 'Payment successful! Your admission is confirmed.')
        return redirect('student_dashboard')

    return render(request, 'pay_fees.html', {'application': application})


# --- Admin Flows ---

def is_admin(user):
    return user.is_superuser or (hasattr(user, 'userprofile') and user.userprofile.role == 'admin')

@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        return redirect('student_dashboard')
    
    applications = ApplicationForm.objects.all().order_by('-submitted_at')
    
    context = {
        'total_apps': applications.count(),
        'pending_apps': applications.filter(status='Pending').count(),
        'approved_apps': applications.filter(status='Merit Approved').count(),
        'admitted_apps': applications.filter(status='Paid').count(),
        'applications': applications[:10] # show recent 10
    }
    return render(request, 'admin_dashboard.html', context)

@login_required
def admin_verify(request, app_id):
    if not is_admin(request.user):
        return redirect('student_dashboard')

    application = get_object_or_404(ApplicationForm, id=app_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            application.status = 'Merit Approved'
            application.save()
            messages.success(request, f'Application {application.id} approved for merit list.')
        elif action == 'reject':
            application.status = 'Rejected'
            application.save()
            messages.success(request, f'Application {application.id} rejected.')
        return redirect('admin_dashboard')

    return render(request, 'admin_verify.html', {'application': application})

@login_required
def merit_list(request):
    if not is_admin(request.user):
        return redirect('student_dashboard')

    # Get applications that are either verified or approved, ordered by 12th marks descending
    applications = ApplicationForm.objects.filter(status__in=['Documents Verified', 'Merit Approved', 'Paid']).order_by('-marks_12th')
    return render(request, 'merit_list.html', {'applications': applications})

@login_required
def manage_courses(request):
    if not is_admin(request.user):
        return redirect('student_dashboard')

    courses = Course.objects.all()
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course added successfully.')
            return redirect('manage_courses')
    else:
        form = CourseForm()

    return render(request, 'manage_courses.html', {'courses': courses, 'form': form})
