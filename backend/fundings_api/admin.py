from django.contrib import admin
from .models import UserModel, SessionModel, PaymentModel, TgUserModel

# Register your models here.

@admin.register(UserModel)
class UserModeAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_subscription_level', 'user_subscription_expire']

@admin.register(SessionModel)
class SessionModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'user_agent', 'ip_address']

@admin.register(PaymentModel)
class PaymentModelAdmin(admin.ModelAdmin):
    list_display = ['user_tg_id', 'pay_amount', 'pay_status', 'tariff', 'pay_created_at', 'pay_updated_at']

@admin.register(TgUserModel)
class TgUserModelAdmin(admin.ModelAdmin):
    list_display = ['tg_user_id', 'username']