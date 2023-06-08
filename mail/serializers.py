from rest_framework import serializers
from datetime import datetime
from .models import Email, MarkMailUser
from pytz import timezone
from MarkMail.settings import TIME_ZONE
from .check_recaptcha import check_captcha
from django.core.exceptions import ObjectDoesNotExist


class EmailSerializer(serializers.ModelSerializer):
    timestamp = serializers.SerializerMethodField()
    
    class Meta:
        model = Email
        fields = ("id", "sender", "receiver", "timestamp", "content", "subject", "isRead")
        
    
    def get_timestamp(self, obj):
        tz = timezone(TIME_ZONE)
        formatted_timestamp = obj.timestamp.astimezone(tz).strftime(r"%B %d, %Y %I:%M %p")
        
        return formatted_timestamp
    
    
class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    repeat_password = serializers.CharField(read_only=True)
    rescue_code = serializers.IntegerField()
    recaptcha_token = serializers.CharField()
    
    def validate_recaptcha_token(self, value):
        check = check_captcha(value)

        if not check  or check == "False":
            raise serializers.ValidationError("ReCaptcha token is not valid")
        
    def validate_repeat_password(self, value):
        if value.lower() != self.initial_data["password"].lower():
            raise serializers.ValidationError("paswords_not_match")
        
        return value
    
    def validate_rescue_code(self, value):
        if len(str(int(value))) > 16 or len(str(int(value))) <= 0:
            raise serializers.ValidationError("rescuecode_length_error")
        
        return value

    
    class Meta:
        model = MarkMailUser
        fields = ['email', 'password', 'recaptcha_token', 'repeat_password', 'rescue_code']
        
        
    def create(self, validated_data):
        user = MarkMailUser.objects.create_user(email=validated_data["email"], rescue_code=validated_data["rescue_code"])
        user.set_password(validated_data["password"])
        
        user.save()
        
        return user
        
        
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    recaptcha_token = serializers.CharField()
    
    def validate_recaptcha_token(self, value):
        check = check_captcha(value)

        if not check  or check == "False":
            raise serializers.ValidationError("ReCaptcha token is not valid")
    
    
class UpdateEmailStatusSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField()
    # status = serializers.CharField(max_length=15)
    # isRead = serializers.BooleanField()
    
    
    def validate_status(self, value):
        if value.lower() not in ["inbox", "read", "sent", "archived", "favourites"]:
            raise serializers.ValidationError("Status is not valid")
        
        return value.lower()
    
    class Meta:
        model = Email
        fields = ["id", "status", "isRead"]
        
        
class DeleteEmailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    
    class Meta:
        model = Email
        fields = ["id"]
        
        
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
    recaptcha_token = serializers.CharField()
    
    
    def validate_recaptcha_token(self, value):
        check = check_captcha(value)
        
        if not check  or check == "False":
            raise serializers.ValidationError("ReCaptcha token is not valid")
        
        
class VerifyRescueCodeSerializer(serializers.Serializer):
    rescue_code = serializers.IntegerField()
    email = serializers.CharField()
    
    
class ResetPasswordSerializer(VerifyRescueCodeSerializer):
    password = serializers.CharField()
    repeat_password = serializers.CharField()
    
    def validate_repeat_password(self, value):
        if value != self.initial_data["password"]:
            raise serializers.ValidationError("Passwords do not match")
        
        return value
    
    
class CreateEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ["content", "receiver", "subject"]
        
        
class CheckEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        splitted_email = str(value).split("@")
        
        if splitted_email[1] != "markmail.com":
            raise serializers.ValidationError("Not a markmail address")
        
        return value