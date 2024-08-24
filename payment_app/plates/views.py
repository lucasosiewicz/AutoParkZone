from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from plates.models import Plate
from plates.forms import PlateForm

# Create your views here.
#def home(request):
#    return render(request, 'plates/index.html', {'form': form, 'results': results})

def search(request):
    form = PlateForm(request.GET or None)
    results = []
    if form.is_valid():
        code = form.cleaned_data['code']
        results = Plate.objects.filter(plate_code__icontains=code)

    return render(request, 'index.html', {'form': form, 'results': results})
    

def plate_details(request, pk):
    plate = get_object_or_404(Plate, pk=pk)
    return render(request, 'plate_details.html', {'plate': plate})

