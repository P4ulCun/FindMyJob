from django.urls import path

from . import views

urlpatterns = [
    path('', views.job_preference_detail, name='job-preference-detail'),
    path('unsubscribe/<str:token>/', views.unsubscribe_digest, name='unsubscribe-digest'),
]
