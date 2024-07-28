from typing import Any
from django.http import JsonResponse

class SuccessResponse:
    def __init__(self, data, status=200):
        response = {
            "result" : True,
            "data" : data
        }
        return JsonResponse(response, status=status)
    

class MessageResponse:
    def __init__(self, msg, status=200):
        response = {
            "result" : True,
            "message" : msg
        }
        return JsonResponse(response, status=status)


class ErrorResponse:
    def __init__(self, msg, status=400):
        response = {
            "result" : False,
            "error" : msg
        }
        return JsonResponse(response, status=status)
    

class UnauthorizedResponse:
    def __init__(self, msg, *args, **kwargs):
        response = {
            "result" : True,
            "error" : msg or "Unauthorized Access"
        }
        return JsonResponse(response, status=403)