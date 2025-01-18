from common.utils.responses import UnauthorizedResponse
from django.conf import settings
from django.views import View
from django.views.decorators.csrf import csrf_exempt
import jwt


class JWTRequiredMixin:
    '''
    Decodes JWT and attaches claimset to request.
    We will avoid using Django's middleware that attaches a User object.
    '''
    def dispatch(self, request, *args, **kwargs):
        a_token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]

        try:
            claimset = jwt.decode(a_token, settings.JWT_SECRET, algorithms=["HS256"], verify_signature=True)
        except Exception as e:
            return UnauthorizedResponse()
        
        request.META['user'] = claimset
        return super().dispatch(request, *args, **kwargs)


class APIView(View):
    @classmethod
    def as_view(cls, **initkwargs):
        '''Exempts csrf middleware in favour of JWTAuth'''
        view = super().as_view(**initkwargs)
        view.cls = cls
        view.initkwargs = initkwargs
        return csrf_exempt(view)