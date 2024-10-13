from typing import Any
from django.http import JsonResponse
from django.core.paginator import Paginator


def PaginatedResponse(request, qset, status=200):
    page_no = int(request.GET.get('page_no', 1))
    page_size = int(request.GET.get('page_size', 20))

    paginator = Paginator(qset, page_size)
    page = paginator.get_page(page_no)

    response = {
        'result' : True,
        'page_no': page.number,
        'page_count': paginator.num_pages,
        'has_next': page.has_next(),
        'has_previous': page.has_previous(),
        'data': list(page.object_list.values()),
    }
    return JsonResponse(response, status=status)


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
        "result" : False,
        "error" : msg or "Unauthorized Access"
    }
    return JsonResponse(response, status=401)