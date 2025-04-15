"""
URL configuration for moodjournal project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/journal/', permanent=True)),
    path('journal/', include('journal.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
