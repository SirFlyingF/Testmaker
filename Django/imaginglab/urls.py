"""
URL configuration for imaginglab project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views import View
from common.utils.responses import SuccessResponse, MessageResponse
from labreview.urls import xrayurls, mriurls


class healthcheck(View):
    def get(self, request, *args, **kwargs):
        return MessageResponse('I am doing great, thanks for asking')
    
    def post(self, request, *args, **kwargs):
        return SuccessResponse(request.json) if request.json else MessageResponse('No Request Body')
        

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),

    path('how-you-doin/', healthcheck.as_view()),
    path('users/', include('user.urls')),
    path('xray/', include(xrayurls)),
    path('mri/', include(mriurls)),
]
