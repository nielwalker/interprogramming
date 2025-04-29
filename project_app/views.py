from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from heapq import nlargest
import nltk
from django.db import models
from django.shortcuts import render, get_object_or_404 , redirect
from .models import Portfolio, Rating , Intern ,WeeklyReport# Imweeport the Rating model from models.py
import json
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UploadReportForm
from django.utils import timezone
from datetime import timedelta



nltk.download('stopwords')
nltk.download('punkt')
nltk.download('punkt_tab')


@login_required
def student_dashboard(request):
    return render(request, 'analyzer_app/student_dashboard.html')

def analyze_portfolio(portfolio):
    try:
        # Extract portfolio description
        text = portfolio.description
        sentences = sent_tokenize(text)
        stemmer = PorterStemmer()
        stop_words = set(stopwords.words('english'))
        words = []

        # Tokenize and stem words, excluding stopwords and non-alphabetic tokens
        for sentence in sentences:
            for word in word_tokenize(sentence):
                if word.isalpha() and word.lower() not in stop_words:
                    words.append(stemmer.stem(word.lower()))

        # Calculate word frequency
        freq_dist = nltk.FreqDist(words)
        top_words = [word[0] for word in freq_dist.most_common(10)]

        # Score sentences based on word frequency
        summary = []
        for sentence in sentences:
            sentence_words = word_tokenize(sentence.lower())
            sentence_score = sum(1 for word in sentence_words if stemmer.stem(word) in top_words)
            summary.append((sentence, sentence_score))

        # Generate summary from top-scoring sentences
        summarized_sentences = [sentence[0] for sentence in nlargest(3, summary, key=lambda x: x[1])]
        summary_text = " ".join(summarized_sentences)

        # Example relatedness score (dummy logic)
        relatedness_score = len(top_words) / 10.0

        # Create dummy graph data
        graphs_data = {
            'skills': {
                'labels': ['Technical Skills', 'Communication Skills', 'Relatedness'],
                'values': [len(top_words), 0, relatedness_score * 100],
            }
        }
        graphs_json = json.dumps(graphs_data)

        # Save analysis results to the database
        rating = Rating.objects.create(
            portfolio=portfolio,
            summary=summary_text,
            relatedness_score=relatedness_score,
            technical_skills_score=len(top_words),
            communication_skills_score=0,
            graphs_data=graphs_json,
        )
        print(f"Analysis complete for portfolio ID {portfolio.id}")
        print(f"Summary: {summary_text}")
        print(f"Relatedness Score: {relatedness_score}")
        print(f"Technical Skills: {len(top_words)}")
        print(f"Graphs Data: {graphs_json}")
        print(f"Rating object created with ID: {rating.id}")

    except Exception as e:
        print(f"Error during analysis for portfolio ID {portfolio.id}: {e}")
        # Handle the error appropriately


def intern_logout_view(request):
    """
    Logs out the user and redirects to the login page.
    """
    logout(request)  # Logs out the current user
    return redirect('intern_login')  # Redirect to the login page

def portfolio_analysis_view(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id)
    analyze_portfolio(portfolio)  # This function should save the Rating

    try:
        rating = Rating.objects.filter(portfolio=portfolio).latest('created_at')
    except Rating.DoesNotExist:
        rating = None  # Handle the case where no rating exists yet

    return render(request, 'analyzer_app/portfolio_analysis.html', {
    'portfolio': portfolio,
    'rating': rating,
    'graphs_data': rating.graphs_data  # This is already a JSON string
    })

def home_view(request):
    return render(request, 'analyzer_app/home.html')

def portfolio_list_view(request):
    portfolios = Portfolio.objects.all()  # Or however you want to retrieve your portfolios
    return render(request, 'analyzer_app/portfolio_list.html', {'portfolios': portfolios})


def intern_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('student_dashboard')  # Redirect to the portfolio list or dashboard
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'analyzer_app/intern_login.html')


def upload_portfolio_view(request):
    interns = Intern.objects.all() # Fetch all interns for the dropdown

    if request.method == 'POST':
        intern_id = request.POST.get('intern')
        title = request.POST.get('title')
        description = request.POST.get('description')
        contribution = request.POST.get('contribution')

        if intern_id and title and description and contribution:
            try:
                intern = Intern.objects.get(pk=intern_id)
                Portfolio.objects.create(intern=intern, title=title, description=description, contribution=contribution)
                return redirect('portfolio_list')
            except Intern.DoesNotExist:
                return render(request, 'analyzer_app/upload_portfolio_form.html', {'error': 'Invalid Intern selected.', 'interns': interns})
        else:
            return render(request, 'analyzer_app/upload_portfolio_form.html', {'error': 'Please fill in all required fields.', 'interns': interns})
    else:
        return render(request, 'analyzer_app/upload_portfolio_form.html', {'interns': interns})
    


def overview_reports(request):
    reports = WeeklyReport.objects.filter(student=request.user).order_by('week_number')
    context = {'reports': reports}
    return render(request, 'overview_reports.html', context)


def upload_report(request, week_number):
    today = timezone.now().date()
    # Assuming the week starts on a Monday. Adjust as needed.
    start_of_week = today - timedelta(days=today.weekday())
    upload_deadline = start_of_week + timedelta(days=5)  # 5 days to upload

    if today > upload_deadline:
        messages.error(request, f"The upload deadline for Week {week_number} has passed.")
        return redirect('student_dashboard')  # Redirect to the dashboard or an appropriate page

    try:
        existing_report = WeeklyReport.objects.get(student=request.user, week_number=week_number)
        # If a report exists, you might want to handle editing or display a message
        messages.info(request, f"You have already uploaded a report for Week {week_number}.")
        form = UploadReportForm(instance=existing_report) # Populate form for potential editing
    except WeeklyReport.DoesNotExist:
        if request.method == 'POST':
            form = UploadReportForm(request.POST, request.FILES, week_number=week_number, student=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, f"Report for Week {week_number} uploaded successfully!")
                return redirect('student_dashboard')
        else:
            form = UploadReportForm(week_number=week_number, student=request.user)

    context = {'form': form, 'week_number': week_number}
    return render(request, 'upload_report.html', context)
