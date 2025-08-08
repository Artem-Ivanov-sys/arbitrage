from django.db import models
from mongoengine import Document, DateTimeField, DictField
from datetime import datetime
# from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

class MainFundingModel(Document):
    time = DateTimeField(default=datetime.now)
    fundings = DictField(
        field=DictField(
            field=DictField()
        )
    )

class UserModel(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='user_data')
    user_tg_id = models.IntegerField()
    user_subscription_level = models.CharField(max_length=63)
    user_subscription_expire = models.DateTimeField(auto_now=False, auto_now_add=False)

class SessionModel(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=256, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

class PaymentModel(models.Model):
    user = models.ForeignKey(get_user_model(), related_name="user", on_delete=models.CASCADE)

    class Meta:
        pass

# Create your models here.
