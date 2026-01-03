"""
Weather data models for storing historical weather information.
"""
from django.db import models
from django.utils import timezone


class WeatherData(models.Model):
    """
    Model to store historical weather data for analytics.
    """
    city = models.CharField(max_length=100, db_index=True)
    country = models.CharField(max_length=100, blank=True)
    temperature = models.FloatField(help_text="Temperature in Celsius")
    feels_like = models.FloatField(null=True, blank=True)
    humidity = models.IntegerField(help_text="Humidity percentage")
    pressure = models.IntegerField(help_text="Pressure in hPa")
    wind_speed = models.FloatField(help_text="Wind speed in m/s")
    wind_direction = models.IntegerField(null=True, blank=True, help_text="Wind direction in degrees")
    visibility = models.IntegerField(null=True, blank=True, help_text="Visibility in meters")
    cloudiness = models.IntegerField(default=0, help_text="Cloudiness percentage")
    rain_volume = models.FloatField(null=True, blank=True, help_text="Rain volume in mm (last 3 hours)")
    snow_volume = models.FloatField(null=True, blank=True, help_text="Snow volume in mm (last 3 hours)")
    description = models.CharField(max_length=200, blank=True)
    icon = models.CharField(max_length=10, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    date = models.DateField(default=timezone.now, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['city', 'date']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.city} - {self.temperature}°C - {self.timestamp}"


class ForecastData(models.Model):
    """
    Model to store forecast data for future reference.
    """
    city = models.CharField(max_length=100, db_index=True)
    country = models.CharField(max_length=100, blank=True)
    forecast_date = models.DateTimeField(db_index=True)
    temperature = models.FloatField()
    feels_like = models.FloatField(null=True, blank=True)
    humidity = models.IntegerField()
    pressure = models.IntegerField()
    wind_speed = models.FloatField()
    description = models.CharField(max_length=200, blank=True)
    icon = models.CharField(max_length=10, blank=True)
    rain_probability = models.IntegerField(null=True, blank=True, help_text="Rain probability percentage")
    stored_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['forecast_date']
        indexes = [
            models.Index(fields=['city', 'forecast_date']),
        ]
    
    def __str__(self):
        return f"{self.city} - {self.forecast_date} - {self.temperature}°C"

