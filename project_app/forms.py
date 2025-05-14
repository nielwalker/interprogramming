from django import forms
from .models import Intern, Portfolio, WeeklyReport, WeekReport

class InternForm(forms.ModelForm):
    class Meta:
        model = Intern
        fields = ['username', 'password', 'first_name', 'last_name', 'section']

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['description', 'contribution']


class UploadReportForm(forms.ModelForm):
    class Meta:
        model = WeeklyReport
        fields = ['intern', 'week', 'date', 'hours', 'activities', 'score', 'learnings']

    def __init__(self, *args, **kwargs):
        self.week_number = kwargs.pop('week_number', None)
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.week_number = self.week_number
        instance.student = self.student
        if commit:
            instance.save()
        return instance


class WeekReportForm(forms.ModelForm):
    class Meta:
        model = WeekReport
        fields = ['week', 'date', 'hours', 'activities', 'score', 'learnings']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'hours': forms.NumberInput(attrs={'min': 0}),
            'activities': forms.Textarea(attrs={'rows': 3}),
            'learnings': forms.Textarea(attrs={'rows': 3}),
        }