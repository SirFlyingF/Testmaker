from django.urls import path
from . import views

xrayurls = [
    path('lab/', views.XRayLabAPI.as_view()),
    path('review/', views.XReviewAPI.as_view()),
]


mriurls = [
    path('lab/', views.MRLabAPI.as_view()),
    path('review/', views.MReviewAPI.as_view()),
]