import json

from django.db import models
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from extended_field import ListField
from django.conf import settings
from django.utils import timezone

# Create your models here.
class UserDetail(models.Model):
    user_fav_category = ListField(null=True,blank=True)
    user = models.OneToOneField(User)
    
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural=u'User Details'
        
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    activation_key = models.CharField(max_length=40, blank=True)
    password_token = models.CharField(max_length=40, blank=True,null=True)
    key_expires = models.DateTimeField(default=timezone.now()+timedelta(days=settings.USER_ACTIVATION_MAIL_EXPIRY_PERIOD))
      
    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural=u'User profiles'
        
    @property
    def key_expired(self):
        return self.key_expires < timezone.now()
    
    @property
    def password_key_expired(self):
        return False if self.password_token else True
        
