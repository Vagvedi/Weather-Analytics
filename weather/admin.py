"""
Admin configuration for weather models.
"""
from django.contrib import admin
from .models import WeatherData, ForecastData


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['city', 'country', 'temperature', 'humidity', 'wind_speed', 'timestamp']
    list_filter = ['city', 'country', 'date', 'timestamp']
    search_fields = ['city', 'country', 'description']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(ForecastData)
class ForecastDataAdmin(admin.ModelAdmin):
    list_display = ['city', 'country', 'temperature', 'forecast_date', 'stored_at']
    list_filter = ['city', 'country', 'forecast_date']
    search_fields = ['city', 'country']
    readonly_fields = ['stored_at']

