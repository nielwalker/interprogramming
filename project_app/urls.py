from django.urls import path
from . import views
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views





urlpatterns = [
    path('', views.intern_login_view, name='intern_login'), # Consider renaming this for clarity
    path('portfolios/', views.portfolio_list_view, name='portfolio_list'),
    path('portfolio/<int:portfolio_id>/analyze/', views.portfolio_analysis_view, name='portfolio_analysis'),
    path('upload/', views.upload_portfolio_view, name='upload_portfolio'),
    path('logout/', views.intern_logout_view, name='logout'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('upload/<int:week_number>/', views.upload_report, name='upload_report'),
    path('overview/', views.overview_reports, name='overview_reports'),
    path('accounts/login/', views.intern_login_view, name='login'), # Assuming views.intern_login_view is your login view
]