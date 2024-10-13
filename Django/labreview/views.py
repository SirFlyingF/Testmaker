from django.views import View
from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from django.conf import settings
from common.models import MediaFile
from common.utils.responses import *
from common.utils.permissions import JWTRequiredMixin

# Create your views here.


class XRayModuleChoicesAPI(JWTRequiredMixin, View):
    '''API to get the module choices for XRLab'''
    def get(self, request, *args, **kwargs):
        choices = [
            {'id' : choice[0],  'display_text' : choice[1]}
            for choice in MediaFile.XRay_choices
        ]
        return SuccessResponse(choices, status=200)


class XRayLabAPI(JWTRequiredMixin, View):
    '''API for serving XRay Study Material'''
    def get(self, request, *args, **kwargs):
        module = request.GET.get('module_id')
        title = request.GET.get('title')
        file_id = request.GET.get('file_id')

        mediafile_qset = MediaFile.objects.all()

        if module:
            mediafile_qset = mediafile_qset.filter(module=module)
        if title:
            mediafile_qset = mediafile_qset.filter(title__icontains=title)
        if file_id:
            mediafile_qset = mediafile_qset.filter(pk=file_id)

        mediafile_qset = mediafile_qset.order_by('pk').values()
        return PaginatedResponse(request, mediafile_qset)


class XReviewAPI(JWTRequiredMixin, View):
    pass


class MRLabAPI(JWTRequiredMixin, View):
    pass


class MReviewAPI(JWTRequiredMixin, View):
    pass