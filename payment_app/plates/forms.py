from django import forms

class PlateForm(forms.Form):
    code = forms.CharField(label='Plate code', max_length=10)