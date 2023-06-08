from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from datetime import datetime
# Create your models here.

class MarkMailUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("E-Mail is missing!")
        
        email = self.normalize_email(email=email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        
        return user
    
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, password, **extra_fields)
    
    
class MarkMailUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    rescue_code = models.IntegerField(null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = MarkMailUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["rescue_code"]
    
    def __str__(self):
        return f"{self.email}"
    
    
class Email(models.Model):
    STATUS_CHOICES = (
        ("inbox", "Inbox"),
        ("sent", "Sent"),
        ("archived", "Archived"),
        ("favourites", "Favourites")
        
    )
    
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(MarkMailUser, on_delete=models.CASCADE, related_name="email_sender", to_field="email")
    receiver = models.ForeignKey(MarkMailUser, on_delete=models.CASCADE, related_name="email_receiver", to_field="email")
    content = models.TextField(max_length=2500, blank=True)
    subject = models.CharField(max_length=100, default="No Subject")
    isRead = models.BooleanField(default=False)
    status = models.CharField(choices=STATUS_CHOICES, max_length=15, default="inbox", null=True, blank=True)
    timestamp = models.DateTimeField(auto_created=True, auto_now_add=True)
    
    def formatted_datetime(self):
        return self.timestamp.strftime(r"%B %d, %Y %I:%M %p")
    
    
    def __str__(self):
        return f"ID: {self.id}, Sender: {self.sender}@{self.formatted_datetime()}"