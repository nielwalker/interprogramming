from django.db import models

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