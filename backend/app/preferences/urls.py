from django.urls import path

from . import views

urlpatterns = [
    path('', views.job_preference_detail, name='job-preference-detail'),
]
