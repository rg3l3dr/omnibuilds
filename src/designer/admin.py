from django.contrib import admin
from django.contrib.admin import AdminSite
from .models import *
# Register your models here.

admin.site.register(Signup)
admin.site.register(License)
admin.site.register(SubPlan)
admin.site.register(Profile)
admin.site.register(UserProfile)
admin.site.register(TeamProfile)
admin.site.register(Project)
