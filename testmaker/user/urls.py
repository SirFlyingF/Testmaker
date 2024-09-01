from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserDetailAPI.as_view()),
    path('register/', views.RegisterAPI.as_view()),
    path('verify-user/', views.VerifyRegisterUserAPI.as_view(), name='verify-user'),
    path('login/', views.LoginAPI.as_view()),
    path('refresh-token/', views.RefreshAPI.as_view()),
    path('forgot-password/', views.PasswordResetMailerAPI.as_view()),
    path('reset-password/', views.NewPasswordAPI.as_view()),
]
