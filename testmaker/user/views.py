from django.views import View
from django.conf import settings
from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from common.models import User
from common.utils.responses import *
from common.utils.permissions import CustomLoginRequiredMixin
from datetime import datetime, timedelta
import jwt
import random
import json

# Create your views here.

class RegisterAPI(View):
    '''API to create user and send email for verification'''
    def post(self, request):
        request_data = json.loads(request.body)
        if not all(field in request_data for field in ['email', 'password1', 'password2', 'display_name']):
            return ErrorResponse('Misseing required values')
        
        email = request_data.get('email')
        password1, password2 = request_data.get('password1'), request_data.get('password2')
        display_name = request_data.get('display_name')

        if password1 != password2:
            return ErrorResponse('Password did not match Confirm Password')
        
        # Below logic allows 'resend verification email' using same endpoint
        # This also allows reusing same email id for a user that previosuly may have signed up
        # but didnt verify.
        if uzr := User.objects.filter(email=email).first():
            if uzr.is_active:
                return ErrorResponse('User already exists. Try forget password')
            else:
                uzr.display_name = display_name
                uzr.set_password(password1)
                uzr.save()
        else:
            uzr = User.objects.create_user(email=email, password=password1, display_name=display_name)

        token = jwt.encode({'id' : uzr.id, 'exp' : (datetime.now()+timedelta(minutes=5))}, settings.JWT_SECRET, algorithm="HS256")
        verification_link = f"http://{settings.DOMAIN}{reverse_lazy('verify-user')}?token={token}"

        from_email = f'{settings.EMAIL_HOST_USER}'
        to_email = uzr.email
        subject = 'Email Verification for new User'
        body  = f"Hello {uzr.display_name},\n\n"
        body +=  "We hope this email find you well. Please visit the below link to verify yout email. Without verification your account will not be active\n\n"
        body += f"Verification Link : {verification_link}\n\n"
        body +=  "Please note that the link will expire after 5 minutes from the time of generation.\n\n"
        body +=  "Regards"
        try:
            EmailMessage(subject, body, from_email, [to_email]).send()
        except Exception as e:
            return ErrorResponse(str(e), 500)
        return MessageResponse('Successfully sent temporary password to email')


class VerifyRegisterUserAPI(View):
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return ErrorResponse('Verification token not found')
        
        try:
            claimset = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"], verify_signature=True)
        except Exception as e:
            return ErrorResponse('Verification Link Expired')
        
        try:
            if uzr := User.objects.filter(id=claimset.get('id')).first():
                uzr.is_active = True
                uzr.save()
                return MessageResponse('Email verified successfully. Please Login to continue')
            return ErrorResponse('Invalid verification link')
        except Exception as e:
            return ErrorResponse(str(e), 500)


class LoginAPI(View):
    def post(self, request):
        try:
            request_data = json.loads(request.body)
            email, password = request_data.get('email'), request_data.get('password')
            now = datetime.now()
            
            user = User.objects.filter(email=email).first()
            if not user:
                return ErrorResponse(f'User does not exist')
            if not user.check_password(password):
                return ErrorResponse(f'Password is invalid')

            user.last_login = now
            user.save()
            
            claimset = {
                'id' : user.id,
                'email' : user.email,
                'isActive' : user.is_active,
                'isStaff' : user.is_staff,
                'isSuperuser' : user.is_superuser,
                'type' : 'ACCESS',
                'exp' : now+timedelta(minutes=5)
            }
            a_token = jwt.encode(claimset, settings.JWT_SECRET, algorithm="HS256")

            claimset['type'] = 'REFRESH'
            claimset['exp'] = now+timedelta(minutes=60)
            r_token = jwt.encode(claimset, settings.JWT_SECRET, algorithm="HS256")

            ctx = {
                'access' : a_token,
                'refresh' : r_token
            }
            return SuccessResponse(ctx, 200)
        except Exception as e:
            return ErrorResponse(str(e), 500)


class RefreshAPI(View):
    '''API to refresh JWT token'''
    def post(self, request):
        request_data = json.loads(request.body)
        r_token = request_data.get('refresh')
        try:
            claimset = jwt.decode(r_token, settings.JWT_SECRET, algorithms=["HS256"], verify_signature=True)
        except Exception as e:
            return UnauthorizedResponse('Token Expired')

        claimset['exp'] = datetime.now() + timedelta(minutes=60)
        r_token = jwt.encode(claimset, settings.JWT_SECRET, algorithm="HS256")

        claimset['type'] = 'ACCESS'
        claimset['exp'] = datetime.now()+timedelta(minutes=10)
        a_token = jwt.encode(claimset, settings.JWT_SECRET, algorithm="HS256")

        ctx = {
            'access' : a_token,
            'refresh' : r_token
        }
        return SuccessResponse(ctx, 200)


class PasswordResetMailerAPI(View):
    '''Sends new randomly generated new password to email'''
    def post(self, request):
        request_data = json.loads(request.body)
        email = request_data.get('email')
        if uzr := User.objects.filter(email=email).first():
            new_password = f'{uzr.display_name}-{random.randint(1000,9999)}'
            uzr.set_password(new_password)
            uzr.save()

            from_email = f'{settings.EMAIL_HOST_USER}'
            to_email = uzr.email
            subject = 'Password Reset'
            body  = f"Hello {uzr.display_name},\n\n"
            body +=  "Below is a randomly generated password. You can use this to login to your account. We suggest you set a new password as soon as possible.\n\n"
            body += f"New Password : {new_password}\n\n"
            body +=  "Regards"
            try:
                EmailMessage(subject, body, from_email, [to_email]).send()
            except Exception as e:
                return ErrorResponse(str(e), 500)
            return MessageResponse('Successfully sent temporary password to email')
        return ErrorResponse('User does not exist', 400)


class NewPasswordAPI(CustomLoginRequiredMixin, View):
    '''API to set a randomly generated new password'''
    def post(self, request):
        request_data = json.loads(request.body)
        old_password = request_data.get('oldPassword')
        password1, password2 = request_data.get('password1'), request_data.get('password2')

        if not password1 or not password2 or not (password1 == password2):
            return ErrorResponse('New password did not match confirm password', 400)
        try:
            user = request.META.get('user')
            uzr = User.objects.filter(email=user.get('email')).first()
            if uzr.check_password(old_password):
                uzr.set_password(password1)
                uzr.save()
            else:
                return ErrorResponse('Old password is incorrect', status=400)
        except Exception as e:
            return ErrorResponse(str(e), 500)    
        return MessageResponse('Password updated successfully')


class UserDetailAPI(CustomLoginRequiredMixin, View):
    '''API to manipulate User data'''
    def put(self, request):
        user_id = request.META.get('user').get('id')
        request_data = json.loads(request.body)
        try:
            if uzr := User.objects.filter(pk=user_id).first():
                uzr.display_name = request_data.get('displayName')
                uzr.save()
            else:
                return ErrorResponse('User not found', status=404)
        except Exception as e:
            return ErrorResponse(str(e), 500)
        return MessageResponse('User details updated successfully')
    

    def get(self, request):
        user_id = request.META.get('user').get('id')
        try:
            if uzr := User.objects.filter(pk=user_id).first():
                resp = {
                    'id': uzr.pk,
                    'email': uzr.email,
                    'displayName' : uzr.display_name,
                    'dateJoined' : uzr.date_joined,
                    'lastLogin' : uzr.last_login
                }
            else:
                return ErrorResponse('User not found', status=404)
        except Exception as e:
            return ErrorResponse(str(e), 500)
        return SuccessResponse(data=resp, status=200)