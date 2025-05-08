from django.urls import path
from . import views
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path('', views.intern_login_view, name='intern_login'),
    path('portfolios/', views.portfolio_list_view, name='portfolio_list'),
    path('portfolio/<int:portfolio_id>/analyze/', views.portfolio_analysis_view, name='portfolio_analysis'),
    path('upload/', views.upload_portfolio_view, name='upload_portfolio'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('upload/<int:week_number>/', views.upload_report, name='upload_report'),
    path('overview/', views.overview_reports, name='overview_reports'),
    path('accounts/login/', views.intern_login_view, name='login'),
    path('add-week-report/', views.add_week_report, name='add_week_report'),
    path('success/', views.success, name='success'), 
    path('get-week-reports/', views.get_week_reports, name='get_week_reports'),
    path('update-week-report/', views.update_week_report, name='update_week_report'),
    path('coordinator/login/', views.coordinator_login_view, name='coordinator_login'),
    path('chairman/login/', views.chairman_login_view, name='chairman_login'),
    path('coordinator/register/', views.coordinator_register_view, name='coordinator_register'),
    path('coordinator/dashboard/', views.coordinator_dashboard_view, name='coordinator_dashboard'),
    path('coordinator/logout/', LogoutView.as_view(next_page='coordinator_login'), name='coordinator_logout'),
]