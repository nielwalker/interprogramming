from django.db import models
from django.contrib.auth.models import User



class WeeklyReport(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    week_number = models.IntegerField()
    submission_date = models.DateField(auto_now_add=True)
    report_file = models.FileField(upload_to='reports/')  # Stores the PDF file
    date_and_hours = models.CharField(max_length=255, blank=True, null=True)
    activities_tasks = models.TextField(blank=True, null=True)
    score_accomplished_targets = models.CharField(max_length=255, blank=True, null=True)
    new_learnings = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'week_number')  # Ensure only one report per student per week

    def __str__(self):
        return f"Report for Week {self.week_number} - {self.student.username}"


class Intern(models.Model):
    name = models.CharField(max_length=255)
    course = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Portfolio(models.Model):
    intern = models.ForeignKey(Intern, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)  # Add this line
    description = models.TextField()
    contribution = models.TextField()  # Detailed contribution during OJT
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.intern.name}'s Portfolio on {self.upload_date.strftime('%Y-%m-%d')}"

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