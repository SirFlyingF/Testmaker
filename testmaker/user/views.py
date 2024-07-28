from django.views import View
from django.conf import settings
from .models import User, AuthToken
from testmaker.utils.responses import *
from testmaker.utils.permissions import CustomLoginRequiredMixin
from datetime import datetime, timedelta
import jwt

# Create your views here.

class RegisterAPI(View):
    '''API to create user and email for verification'''
    def post(self, request):
        pass


class RegisterPaymentRedirectAPI(View):
    '''API to redirect to payment gateway upon email verification'''
    def post(self, request):
        pass


class VerifyPaymentWebhookAPI(View):
    '''API to redirect to login or error page upon payment verification'''
    def post(self, request):
        pass


class LoginAPI(View):
    def post(self, request):
        try:
            email, password = request.data.get('email'), request.data.get('password')
            
            user = User.objects.filter(email=email).first()
            if not user:
                return ErrorResponse(f'User does not exist')
            if not user.check_password(password):
                return ErrorResponse(f'Incorrect password')
            
            claimset = {
                'email' : user.email,
                'isActive' : user.is_active,
                'isStaff' : user.is_staff,
                'isSuperuser' : user.is_superuser,
                'type' : 'ACCESS',
                'validity' : datetime.now() + timedelta(minutes=10)
            }
            a_token = jwt.encode(claimset, settings.JWT_SECRET, algorithm="HS256")

            claimset['type'] = 'REFRESH'
            claimset['validity'] = datetime.now() + timedelta(minutes=60)
            r_token = jwt.encode(claimset, settings.JWT_SECRET, algorithm="HS256")

            ctx = {
                'access' : a_token.token,
                'refresh' : r_token.token
            }
            return SuccessResponse(ctx, 200)
        except Exception as e:
            return ErrorResponse(str(e), 500)


class RefreshAPI(View):
    def post(self, request):
        r_token = request.data.get('refresh')
        try:
            claimset = jwt.decode(r_token, settings.JWT_SECRET, algorithms=["HS256"], verify_signature=True)
        except Exception as e:
            return UnauthorizedResponse('Token Expired')

        claimset['validity'] = datetime.now() + timedelta(minutes=60)
        r_token = jwt.encode(claimset, settings.JWT_SECRET, algorithm="HS256")

        claimset['type'] = 'ACCESS'
        claimset['validity'] = datetime.now() + timedelta(minutes=10)
        a_token = jwt.encode(claimset, settings.JWT_SECRET, algorithm="HS256")

        ctx = {
            'access' : a_token.token,
            'refresh' : r_token.token
        }
        return SuccessResponse(ctx, 200)


class PasswordResetMailerAPI(View):
    '''Sends new randomly generated new password to email'''
    def post(self, request):
        email = request.data.get('email')
        if not User.objects.filter(email=email).exists():
            return ErrorResponse('User does not exist', 400)
        
        return MessageResponse('Successfully sent temporary password to email')


class NewPasswordAPI(CustomLoginRequiredMixin, View):
    def post(self, request):
        n_password1, n_password2 = request.data.get('newPassword2'), request.data.get('newPassword2')
        if not (n_password1 == n_password2):
            return ErrorResponse('New password did not match confirm password', 400)
        
        claimset = request.META.get('claimset')
        try:
            user = User.objects.filter(email=claimset.get('email'))
            user.set_password(n_password1)
            user.save()
        except Exception as e:
            return ErrorResponse(str(e), 500)    
        return MessageResponse('Password updated successfully')
