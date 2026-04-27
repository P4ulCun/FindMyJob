from django.urls import path

from . import views

urlpatterns = [
    path('upload/', views.upload_cv, name='cv-upload'),
    path('me/', views.cv_me, name='cv-me'),
    path('<int:pk>/', views.cv_detail, name='cv-detail'),
    path('tailor/', views.tailor_cv, name='cv-tailor'),
    path('tailored/', views.tailored_cv_list, name='cv-tailored-list'),
]
