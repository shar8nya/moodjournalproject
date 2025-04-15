from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('entries/', views.entry_list, name='entry-list'),
    path('entries/create/', views.create_entry, name='create-entry'),
    path('entries/<str:date>/edit/', views.edit_entry, name='edit-entry'),
    path('entries/<str:date>/', views.entry_detail, name='entry-detail'),
    path('register/', views.register, name='register'),
    path('analytics/', views.mood_analytics, name='mood-analytics'),
    path('tailored-content/', views.tailored_content, name='tailored-content'),
    path('api/mood-data/', views.mood_data_api, name='mood-data-api'),
]
