from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from plates.forms import PlateForm
from plates.models import Plate, PlatePaid
from datetime import datetime
import pytz

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
    now = datetime.now()
    return render(request, 'plate_details.html', {'plate': plate, 'now': now})


def pay(request, pk):
    if request.method == 'POST':
        plate = get_object_or_404(Plate, pk=pk)
        cost = 0

        cost = (datetime.now(pytz.utc) - plate.arrived_at).seconds / 60
        cost = cost * 0.05
        cost = round(cost, 2)
        plate_paid = PlatePaid(plate_code=plate.plate_code, arrived_at=plate.arrived_at, cost=cost)
        plate_paid.save()
        plate.delete()

        return render(request, 'pay.html', {'plate_paid': plate_paid, 'cost': cost})
