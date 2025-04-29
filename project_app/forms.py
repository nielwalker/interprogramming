from django import forms
from .models import Intern, Portfolio

class InternForm(forms.ModelForm):
    class Meta:
        model = Intern
        fields = ['name', 'course']

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['description', 'contribution']