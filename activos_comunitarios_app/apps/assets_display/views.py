from django.shortcuts import render
from ..comunity_assets.models import ComunityAsset
from django.http import JsonResponse

# Create your views here.


def display_assets(request):
    return render(request,'comunity_assets/display_assets.html')


def users_assets_view(request):
    return render(request, 'anom_user/user_assets_views.html')


