from typing import Any
from django.http import JsonResponse


def SuccessResponse(data, status=200):
    response = {
        "result" : True,
        "data" : data
    }
    return JsonResponse(response, status=status)


def MessageResponse(msg, status=200):
    response = {
        "result" : True,
        "message" : msg
    }
    return JsonResponse(response, status=status)


def ErrorResponse(msg, status=400):
    response = {
        "result" : False,
        "error" : msg
    }
    return JsonResponse(response, status=status)


def UnauthorizedResponse(msg=None, *args, **kwargs):
    response = {
        "result" : True,
        "error" : msg or "Unauthorized Access"
    }
    return JsonResponse(response, status=403)