from django.views import View
from common.models import MediaFile
from common.utils.responses import *
from common.utils.permissions import JWTRequiredMixin

# Create your views here.

class XRayLabAPI(JWTRequiredMixin, View):
    '''API for serving XRay Study Material'''
    def get(request, *args, **kwargs):
        pass


class XReviewAPI(JWTRequiredMixin, View):
    pass


class MRLabAPI(JWTRequiredMixin, View):
    pass


class MReviewAPI(JWTRequiredMixin, View):
    pass