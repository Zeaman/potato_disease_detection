from django import forms
from .models import PotatoImage

class PotatoImageForm(forms.ModelForm):
    class Meta:
        model = PotatoImage
        fields = ['image']