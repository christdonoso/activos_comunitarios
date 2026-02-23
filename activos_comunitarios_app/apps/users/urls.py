"""
URL configuration for activos_comunitarios_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from apps.users import views


urlpatterns = [
    path('', views.index),
    path('profile', views.profile, name='profile'),
    path('create_user', views.create_user, name='create_user'),
    path('edit_user/<int:id>', views.edit_user, name='edit_user'), 
    path('manage_users', views.manage_users, name='manage_users')
]