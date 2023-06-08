from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Email, MarkMailUser
from .serializers import (
    EmailSerializer, UserRegisterSerializer, ChangePasswordSerializer, 
    UpdateEmailStatusSerializer, DeleteEmailSerializer, LoginSerializer, 
    VerifyRescueCodeSerializer, ResetPasswordSerializer, CreateEmailSerializer,
    CheckEmailSerializer
    )
from MarkMail.settings import RECAPTCHA_SECRET
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

"""
    - MarkMail Main Backend written in Django
    
    Hi! My name is Marko Prifti. At this time of creating this project,
    I'm 15 years old. As I get older and eventually gain more knowledge
    about Web Programming with the beautiful web framework for Python 
    Django, I'll do more projects to add to my resume. My goal is to s-
    kip university and get a job in a tech company. With that said,
    
    Happy creating more web apps! 
    
    
    
"""


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_emails(request):
    if request.data["emailClass"] == "inbox":
        model = Email.objects.filter(receiver=request.user, status="inbox")
        serializer = EmailSerializer(model, many=True)

        return Response(serializer.data, HTTP_200_OK)
    
    elif request.data["emailClass"] == "sent":
        model = Email.objects.filter(sender=request.user)
        serializer = EmailSerializer(model, many=True)
        
        return Response(serializer.data, HTTP_200_OK)
    
    elif request.data["emailClass"] == "archived":
        model = Email.objects.filter(receiver=request.user, status="archived")
        serializer = EmailSerializer(model, many=True)
        
        return Response(serializer.data, HTTP_200_OK)
    
    elif request.data["emailClass"] == "favourites":
        model = Email.objects.filter(receiver=request.user, status="favourites")
        serializer = EmailSerializer(model, many=True)
        
        return Response(serializer.data, HTTP_200_OK)
    
    
    return Response({"message": "emails_not_found"}, HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    if request.method == "POST":
        serializer = UserRegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({"message": "register_success"}, HTTP_200_OK)
        
        return Response(serializer.errors, HTTP_400_BAD_REQUEST)
    
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        user = request.user
        
        if user.check_password(request.data["old_password"]):
            user.set_password(request.data["new_password"])
            user.save()
            
            return Response({"message": "changepasswd_success"}, HTTP_200_OK)
        
        return Response({"message": "invalid"}, HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def change_status(request):
    serializer = UpdateEmailStatusSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            model = Email.objects.get(id=request.data["id"], receiver=request.user)
        
        except ObjectDoesNotExist:
            return Response({"message": "email_not_found"}, HTTP_400_BAD_REQUEST)
        
        serializer.instance = model
        serializer.save()
         
        return Response({"message": "changestatus_success"}, HTTP_200_OK)
     
    return Response(serializer.errors, HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_email(request):
    serializer = DeleteEmailSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            email = Email.objects.get(id=request.data["id"], receiver=request.user)
            email.delete()

            return Response({"message": "delete_email_success"}, HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"message": "email_not_found"}, HTTP_400_BAD_REQUEST)
        
    return Response(serializer.errors, HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = authenticate(username=request.data["email"], password=request.data["password"])
        
        if user is None:
            return Response({"message": "auth_invalid"}, HTTP_400_BAD_REQUEST)
        
        tokens = RefreshToken.for_user(user)
        
        return Response({
            "refresh": str(tokens),
            "access": str(tokens.access_token)    
        }, HTTP_200_OK)
        
    return Response(serializer.errors, HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_rescue_code(request):
    serializer = VerifyRescueCodeSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = MarkMailUser.objects.get(email=request.data["email"])
    
        except ObjectDoesNotExist:
            return Response({"message": "email_not_found"}, HTTP_400_BAD_REQUEST)
        
        if request.data["rescue_code"] != user.rescue_code:
            return Response({"message": "rescuecode_incorrect"}, HTTP_400_BAD_REQUEST)
        
        return Response({"message": "success"}, HTTP_200_OK)
    
    return Response(serializer.errors, HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = MarkMailUser.objects.get(email=request.data["email"])
    
        except ObjectDoesNotExist:
            return Response({"message": "email_not_found"}, HTTP_400_BAD_REQUEST)
        
        if user.rescue_code != request.data["rescue_code"]:
            return Response({"message": "rescuecode_incorrect"}, HTTP_400_BAD_REQUEST)
        
        user.set_password(request.data["password"])
        user.save()
        
        return Response({"message": "reset_password_success"}, HTTP_200_OK)
    
    return Response(serializer.errors, HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def compose_mail(request):
    serializer = CreateEmailSerializer(data=request.data)
    
    if serializer.is_valid():
        mail = Email.objects.create(receiver=MarkMailUser.objects.get(email=serializer.validated_data.get("receiver")), sender=request.user, content=serializer.validated_data.get("content"), subject=serializer.validated_data.get("subject"))
        serializer.instance = mail
        serializer.save()
        
        return Response({"message": "Created"}, HTTP_201_CREATED)
    
    return Response(serializer.errors, HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def check_email(request):

    
    serializer = CheckEmailSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            MarkMailUser.objects.get(email=request.data["e,ail"])
            
            return Response({"message": "email_exists"}, HTTP_400_BAD_REQUEST)
            
        except ObjectDoesNotExist:
            return Response({"message": "email_ok"}, HTTP_200_OK)
        
    return Response(serializer.errors, HTTP_400_BAD_REQUEST)