from django import forms
from .models import Intern, Portfolio ,WeeklyReport

class InternForm(forms.ModelForm):
    class Meta:
        model = Intern
        fields = ['name', 'course']

class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['description', 'contribution']


class UploadReportForm(forms.ModelForm):
    class Meta:
        model = WeeklyReport
        fields = ['report_file', 'date_and_hours', 'activities_tasks', 'score_accomplished_targets', 'new_learnings']

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