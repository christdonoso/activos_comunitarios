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
from apps.validate_assets import views


urlpatterns = [
    path('validate_assets', views.validate_assets, name='validate_assets'),
    path('approved_assets', views.approved_assets, name='approved_assets'),
    path('rejected_assets', views.rejected_assets, name='rejected_assets'),
    path('process_asset_action', views.process_asset_action, name='process_asset_action'),
]
