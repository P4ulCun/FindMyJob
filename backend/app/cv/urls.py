from django.urls import path

from . import views

urlpatterns = [
    path('upload/', views.upload_cv, name='cv-upload'),
    path('me/', views.cv_me, name='cv-me'),
    path('<int:pk>/', views.cv_detail, name='cv-detail'),
    path('tailor/', views.tailor_cv, name='cv-tailor'),
    path('tailored/', views.tailored_cv_list, name='cv-tailored-list'),
    path('tailored/<int:pk>/', views.tailored_cv_detail, name='cv-tailored-detail'),
    path('cover-letter/generate/', views.generate_cover_letter, name='cover-letter-generate'),
    path('cover-letters/', views.cover_letter_list, name='cover-letter-list'),
    path('cover-letters/<int:pk>/', views.cover_letter_detail, name='cover-letter-detail'),
    path('cover-letters/<int:pk>/download/', views.download_cover_letter, name='cover-letter-download'),
]
