from django.urls import path
from .views import bot_url

urlpatterns = [
    path('projects-collab-bot/', bot_url, name='projects_collab_bot'),
    # Other URL patterns
]