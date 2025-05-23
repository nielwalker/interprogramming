from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from heapq import nlargest
import nltk
from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from .models import Portfolio, Rating, Intern, WeeklyReport, Coordinator, Chairman  ,CoordinatorAssessment# Import the necessary models
import json
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import redirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UploadReportForm, WeekReportForm
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import WeekReport
from django.contrib.auth.models import User


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
    request.session.flush()
    return redirect('intern_login')

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
    if request.session.get('intern_id'):
        return redirect('intern_dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            intern = Intern.objects.get(username=username)
            if check_password(password, intern.password):
                request.session['intern_id'] = intern.id
                return redirect('intern_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        except Intern.DoesNotExist:
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


@csrf_exempt
def add_week_report(request):
    if request.method == 'POST':
        week = request.POST.get('week')
        date = request.POST.get('date')
        hours = request.POST.get('hours')
        activities = request.POST.get('activities')
        score = request.POST.get('score')
        learnings = request.POST.get('learnings')
        if all([week, date, hours, activities, score, learnings]):
            WeekReport.objects.create(
                week=week,
                date=date,
                hours=hours,
                activities=activities,
                score=score,
                learnings=learnings
            )
            return JsonResponse({'message': 'Saved!'})
        return JsonResponse({'error': 'Missing fields'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
def update_week_report(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            report = WeekReport.objects.get(id=data['id'])
            report.date = data['date']
            report.hours = data['hours']
            report.activities = data['activities']
            report.score = data['score']
            report.learnings = data['learnings']
            report.save()
            return JsonResponse({'message': 'Updated!'})
        except WeekReport.DoesNotExist:
            return JsonResponse({'error': 'Report not found'}, status=404)
    return JsonResponse({'error': 'Invalid method'}, status=405)


def success(request):
    return HttpResponse("Week report submitted successfully!")


def get_week_reports(request):
    if request.method == 'GET':
        reports = WeekReport.objects.all().values('id', 'week', 'date', 'hours', 'activities', 'score', 'learnings')
        return JsonResponse(list(reports), safe=False)


def coordinator_login_view(request):
    if request.user.is_authenticated:
        return redirect('coordinator_dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        # You can add extra checks here for coordinator group/role
        if user is not None:
            login(request, user)
            return redirect('coordinator_dashboard')  # Redirect to the dashboard
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'analyzer_app/coordinator_login.html')

def chairman_login_view(request):
    if request.session.get('chairman_id'):
        return redirect('chairman_dashboard')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            chairman = Chairman.objects.get(username=username)
            if check_password(password, chairman.password):
                request.session['chairman_id'] = chairman.id
                return redirect('chairman_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        except Chairman.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'analyzer_app/chairman_login.html')

def chairman_register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST.get('firstname', '')
        last_name = request.POST.get('lastname', '')
        # Check if username exists in Chairman table
        if Chairman.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            Chairman.objects.create(
                username=username,
                password=make_password(password),
                first_name=first_name,
                last_name=last_name
            )
            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('chairman_login')
    return render(request, 'analyzer_app/chairman_register.html')

def coordinator_register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('coordinator_login')
    return render(request, 'analyzer_app/coordinator_register.html')

def coordinator_dashboard_view(request):
    coordinator_id = request.session.get('coordinator_id')
    if not coordinator_id:
        return redirect('coordinator_login')
    interns = Intern.objects.all()
    return render(request, 'analyzer_app/coordinator_dashboard.html', {'interns': interns})

def view_intern_reports(request, intern_id):
    coordinator_id = request.session.get('coordinator_id')
    if not coordinator_id:
        return redirect('coordinator_login')
    intern = get_object_or_404(Intern, id=intern_id)
    reports = WeeklyReport.objects.filter(intern=intern)
    return render(request, 'analyzer_app/view_intern_reports.html', {'intern': intern, 'reports': reports})

@login_required(login_url='coordinator_login')
def student_reports_view(request):
    reports = WeekReport.objects.all()
    return render(request, 'analyzer_app/student_reports.html', {'reports': reports})

# Intern Registration
def intern_register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = make_password(request.POST['password'])
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        section = request.POST['section']
        if Intern.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            Intern.objects.create(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                section=section
            )
            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('intern_login')
    return render(request, 'analyzer_app/intern_register.html')

def intern_dashboard(request):
    intern_id = request.session.get('intern_id')
    if not intern_id:
        return redirect('intern_login')
    intern = Intern.objects.get(id=intern_id)
    reports = WeeklyReport.objects.filter(intern=intern)
    return render(request, 'analyzer_app/intern_dashboard.html', {'intern': intern, 'reports': reports})

def add_weekly_report(request):
    intern_id = request.session.get('intern_id')
    if not intern_id:
        return redirect('intern_login')
    if request.method == 'POST':
        week = request.POST['week']
        date = request.POST['date']
        hours = request.POST['hours']
        activities = request.POST['activities']
        score = request.POST['score']
        learnings = request.POST['learnings']
        WeeklyReport.objects.create(
            intern_id=intern_id,
            week=week,
            date=date,
            hours=hours,
            activities=activities,
            score=score,
            learnings=learnings
        )
        messages.success(request, 'Report added!')
        return redirect('intern_dashboard')
    return render(request, 'analyzer_app/add_weekly_report.html')

def edit_weekly_report(request, report_id):
    intern_id = request.session.get('intern_id')
    report = get_object_or_404(WeeklyReport, id=report_id, intern_id=intern_id)
    if request.method == 'POST':
        report.week = request.POST['week']
        report.date = request.POST['date']
        report.hours = request.POST['hours']
        report.activities = request.POST['activities']
        report.score = request.POST['score']
        report.learnings = request.POST['learnings']
        report.save()
        messages.success(request, 'Report updated!')
        return redirect('intern_dashboard')
    return render(request, 'analyzer_app/edit_weekly_report.html', {'report': report})

def delete_weekly_report(request, report_id):
    intern_id = request.session.get('intern_id')
    report = get_object_or_404(WeeklyReport, id=report_id, intern_id=intern_id)
    report.delete()
    messages.success(request, 'Report deleted!')
    return redirect('intern_dashboard')

def chairman_dashboard_view(request):
    chairman_id = request.session.get('chairman_id')
    if not chairman_id:
        return redirect('chairman_login')
    chairman = Chairman.objects.get(id=chairman_id)
    assessments = CoordinatorAssessment.objects.all()
    return render(request, 'analyzer_app/chairman_dashboard.html', {
        'chairman': chairman,
        'assessments': assessments
    })

def view_coordinator_assessments(request, coordinator_id):
    chairman_id = request.session.get('chairman_id')
    if not chairman_id:
        return redirect('chairman_login')
    coordinator = get_object_or_404(Coordinator, id=coordinator_id)
    assessments = CoordinatorAssessment.objects.filter(coordinator=coordinator)
    return render(request, 'analyzer_app/view_coordinator_assessments.html', {'coordinator': coordinator, 'assessments': assessments})

def chairman_logout_view(request):
    request.session.flush()
    return redirect('chairman_login')
