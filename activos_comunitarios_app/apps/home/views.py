from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'home/index.html')


def conoce_mas(request):
    return render(request, 'home/conoce_mas.html')

def asset_info(request):
    return render(request, 'home/asset_info.html')