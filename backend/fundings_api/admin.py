from django.contrib import admin
from .models import UserModel, SessionModel

# Register your models here.

@admin.register(UserModel)
class UserModeAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_subscription_level', 'user_subscription_expire']

@admin.register(SessionModel)
class SessionModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'user_agent', 'ip_address']