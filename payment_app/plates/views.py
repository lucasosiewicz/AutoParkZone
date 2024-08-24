from django.shortcuts import render
from django.http import HttpResponse
from plates.models import Plate

# Create your views here.
def home(request):
    return HttpResponse('Hello, World!')

def add_plate(request):
    new_plate = Plate(plate_code='ABC123')
    new_plate.save()
    return HttpResponse('Plate added!')
