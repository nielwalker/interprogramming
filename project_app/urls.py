from django.urls import path
from . import views
from django.views.generic import RedirectView

urlpatterns = [
    path('', views.intern_login_view, name='intern_login'),
    path('portfolios/', views.portfolio_list_view, name='portfolio_list'),
    path('portfolio/<int:portfolio_id>/analyze/', views.portfolio_analysis_view, name='portfolio_analysis'),
    path('upload/', views.upload_portfolio_view, name='upload_portfolio'),
    path('logout/', views.intern_logout_view, name='logout'),
]