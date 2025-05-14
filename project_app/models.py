from django.db import models
from django.contrib.auth.models import User
from django import forms

#create database 
#CREATE DATABASE your_db_name CHARACTER SET UTF8MB4;

class Intern(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128, default='')  # Store hashed passwords!
    first_name = models.CharField(max_length=30, default='')
    last_name = models.CharField(max_length=30, default='')
    section = models.CharField(max_length=50, default='')
    # Add other intern-specific fields

    def __str__(self):
        return self.username


class Coordinator(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128, default='')
    first_name = models.CharField(max_length=30, default='')
    last_name = models.CharField(max_length=30, default='')
    section = models.CharField(max_length=50, default='')
    # Add other coordinator-specific fields

    def __str__(self):
        return self.username


class Chairman(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128, default='')
    first_name = models.CharField(max_length=30, default='')
    last_name = models.CharField(max_length=30, default='')
    # Add other chairman-specific fields

    def __str__(self):
        return self.username


class WeeklyReport(models.Model):
    intern = models.ForeignKey(Intern, on_delete=models.CASCADE, related_name='reports')
    week = models.IntegerField()
    date = models.DateField()
    hours = models.IntegerField()
    activities = models.TextField()
    score = models.IntegerField()
    learnings = models.TextField()
    coordinator = models.ForeignKey(Coordinator, on_delete=models.SET_NULL, null=True, blank=True)
    # Add other fields as needed

    def __str__(self):
        return f"Report for Week {self.week} - {self.intern.username}"


class CoordinatorAssessment(models.Model):
    coordinator = models.ForeignKey('Coordinator', on_delete=models.CASCADE)
    intern = models.ForeignKey('Intern', on_delete=models.CASCADE)
    week = models.IntegerField()
    assessment = models.TextField()
    # Add other fields as needed

    def __str__(self):
        return f"Assessment for Week {self.week} - {self.intern.username}"


class ChairmanAssessment(models.Model):
    chairman = models.ForeignKey('Chairman', on_delete=models.CASCADE)
    coordinator_assessment = models.ForeignKey('CoordinatorAssessment', on_delete=models.CASCADE)
    remarks = models.TextField()
    # Add other fields as needed


class Portfolio(models.Model):
    intern = models.ForeignKey(Intern, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)  # Add this line
    description = models.TextField()
    contribution = models.TextField()  # Detailed contribution during OJT
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.intern.username}'s Portfolio on {self.upload_date.strftime('%Y-%m-%d')}"


class Rating(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    summary = models.TextField(blank=True, null=True)
    relatedness_score = models.FloatField(null=True, blank=True)
    technical_skills_score = models.FloatField(null=True, blank=True)
    communication_skills_score = models.FloatField(null=True, blank=True)
    graphs_data = models.JSONField(null=True, blank=True)  # Store data for graphs
    created_at = models.DateTimeField(auto_now_add=True)  # Add this line

    def __str__(self):
        return f"Rating for {self.portfolio}"


class WeekReport(models.Model):
    week = models.CharField(max_length=50)  # Week identifier (e.g., "Week 1")
    date = models.DateField()  # Date of the report
    hours = models.PositiveIntegerField()  # Number of hours
    activities = models.TextField()  # Activities/Tasks
    score = models.CharField(max_length=50)  # Score
    learnings = models.TextField()  # New Learnings

    def __str__(self):
        return f"{self.week} - {self.date}"


class UploadReportForm(forms.ModelForm):
    class Meta:
        model = WeeklyReport
        fields = ['week', 'date', 'hours', 'activities', 'score', 'learnings', 'coordinator']