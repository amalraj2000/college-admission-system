from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Student Flow
    path('', views.student_dashboard, name='student_dashboard'), # Default route for students
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('apply/', views.apply, name='apply'),
    path('upload-documents/', views.upload_documents, name='upload_documents'),
    path('pay-fees/', views.pay_fees, name='pay_fees'),
    
    # Admin Flow
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-verify/<int:app_id>/', views.admin_verify, name='admin_verify'),
    path('merit-list/', views.merit_list, name='merit_list'),
    path('manage-courses/', views.manage_courses, name='manage_courses'),
]
