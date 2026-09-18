from django.contrib import admin
from .models import UserProfile, Course, ApplicationForm, Document, Payment

admin.site.register(UserProfile)
admin.site.register(Course)
admin.site.register(ApplicationForm)
admin.site.register(Document)
admin.site.register(Payment)
