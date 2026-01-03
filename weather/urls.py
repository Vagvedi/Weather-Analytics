"""
URL configuration for weather app.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Main dashboard
    path('', views.dashboard, name='dashboard'),
    
    # REST API endpoints
    path('api/weather/current/', views.api_current_weather, name='api_current_weather'),
    path('api/weather/forecast/', views.api_forecast, name='api_forecast'),
    path('api/analytics/temperature/', views.api_analytics_temperature, name='api_analytics_temperature'),
    path('api/analytics/humidity/', views.api_analytics_humidity, name='api_analytics_humidity'),
    path('api/analytics/rainfall/', views.api_analytics_rainfall, name='api_analytics_rainfall'),
    path('api/analytics/wind/', views.api_analytics_wind, name='api_analytics_wind'),
    path('api/analytics/comparison/', views.api_analytics_comparison, name='api_analytics_comparison'),
]

