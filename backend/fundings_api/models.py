from django.db import models
from mongoengine import Document, StringField, FloatField, DateTimeField, DictField
from datetime import datetime

class MainFundingModel(Document):
    time = DateTimeField(default=datetime.now)
    fundings = DictField(
        field=DictField(
            field=DictField()
        )
    )

# class User(models.Model):
#     pass

class PaymentModel(models.Model):
    user = models.ForeignKey('auth.User', related_name="user", on_delete=models.CASCADE)

    class Meta:
        pass

# Create your models here.
