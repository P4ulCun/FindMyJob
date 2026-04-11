from django.urls import path

from . import views

urlpatterns = [
    path('upload/', views.upload_cv, name='cv-upload'),
    path('<int:pk>/', views.cv_detail, name='cv-detail'),
]
