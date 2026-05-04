from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_jobs, name='search_jobs'),
    path('interactions/', views.job_interactions, name='job_interactions'),
]
