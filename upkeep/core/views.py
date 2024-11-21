# Create your views here.
from django.shortcuts import render

from .models import Area


def areas_view(request):
    if request.method == "GET":
        areas = Area.objects.all()
        return render(request, "core/area_list.html", {"areas": areas})
