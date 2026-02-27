from django.shortcuts import render

# Create your views here.


def create_sector(request):
    return render(request, 'sectorization/create_sector.html')