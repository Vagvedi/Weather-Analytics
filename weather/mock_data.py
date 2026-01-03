"""
Mock data service for weather data when external APIs are unavailable.
Provides realistic weather data for development and fallback scenarios.
"""
from datetime import datetime, timedelta
from django.utils import timezone
import random
import math


class MockWeatherData:
    """
    Generates realistic mock weather data for testing and fallback scenarios.
    """
    
    # Base weather conditions for different cities
    CITY_BASELINES = {
        'london': {'temp': 15, 'humidity': 70, 'wind': 5},
        'new york': {'temp': 20, 'humidity': 65, 'wind': 6},
        'tokyo': {'temp': 22, 'humidity': 75, 'wind': 4},
        'paris': {'temp': 18, 'humidity': 68, 'wind': 5},
        'sydney': {'temp': 25, 'humidity': 60, 'wind': 7},
        'mumbai': {'temp': 30, 'humidity': 80, 'wind': 3},
        'default': {'temp': 20, 'humidity': 70, 'wind': 5},
    }
    
    WEATHER_CONDITIONS = [
        {'description': 'clear sky', 'icon': '01d'},
        {'description': 'few clouds', 'icon': '02d'},
        {'description': 'scattered clouds', 'icon': '03d'},
        {'description': 'broken clouds', 'icon': '04d'},
        {'description': 'shower rain', 'icon': '09d'},
        {'description': 'rain', 'icon': '10d'},
        {'description': 'thunderstorm', 'icon': '11d'},
        {'description': 'snow', 'icon': '13d'},
        {'description': 'mist', 'icon': '50d'},
    ]
    
    @classmethod
    def _get_city_baseline(cls, city):
        """Get baseline weather data for a city."""
        city_lower = city.lower()
        for key, baseline in cls.CITY_BASELINES.items():
            if key in city_lower:
                return baseline
        return cls.CITY_BASELINES['default']
    
    @classmethod
    def _add_variation(cls, base_value, variation_percent=10):
        """Add realistic variation to a base value."""
        variation = base_value * (variation_percent / 100)
        return base_value + random.uniform(-variation, variation)
    
    @classmethod
    def get_current_weather(cls, city, country_code=None):
        """
        Generate mock current weather data.
        
        Args:
            city: City name
            country_code: Optional country code
            
        Returns:
            Dict with current weather data
        """
        baseline = cls._get_city_baseline(city)
        now = timezone.now()
        
        # Simulate day/night temperature variation
        hour = now.hour
        temp_variation = 5 * math.sin((hour - 6) * math.pi / 12)  # Cooler at night
        
        temperature = baseline['temp'] + temp_variation + random.uniform(-3, 3)
        feels_like = temperature - random.uniform(0, 3)
        humidity = baseline['humidity'] + random.uniform(-10, 10)
        humidity = max(30, min(100, humidity))  # Clamp between 30-100
        
        wind_speed = baseline['wind'] + random.uniform(-2, 2)
        wind_speed = max(0, wind_speed)
        
        pressure = 1013 + random.uniform(-20, 20)
        
        # Select weather condition based on humidity
        if humidity > 80:
            condition = random.choice([cls.WEATHER_CONDITIONS[4], cls.WEATHER_CONDITIONS[5], cls.WEATHER_CONDITIONS[6]])
        elif humidity < 50:
            condition = random.choice([cls.WEATHER_CONDITIONS[0], cls.WEATHER_CONDITIONS[1]])
        else:
            condition = random.choice(cls.WEATHER_CONDITIONS)
        
        rain_volume = random.uniform(0, 5) if humidity > 75 else 0
        snow_volume = random.uniform(0, 2) if temperature < 0 and humidity > 70 else 0
        
        return {
            'city': city.title(),
            'country': country_code or 'US',
            'temperature': round(temperature, 1),
            'feels_like': round(feels_like, 1),
            'humidity': int(humidity),
            'pressure': int(pressure),
            'wind_speed': round(wind_speed, 1),
            'wind_direction': random.randint(0, 360),
            'visibility': random.randint(5000, 10000),
            'cloudiness': random.randint(0, 100),
            'description': condition['description'],
            'icon': condition['icon'],
            'rain_volume': round(rain_volume, 2) if rain_volume > 0 else None,
            'snow_volume': round(snow_volume, 2) if snow_volume > 0 else None,
            'timestamp': now.isoformat(),
        }
    
    @classmethod
    def get_forecast(cls, city, country_code=None, days=7):
        """
        Generate mock forecast data.
        
        Args:
            city: City name
            country_code: Optional country code
            days: Number of days to forecast
            
        Returns:
            List of forecast data dicts
        """
        baseline = cls._get_city_baseline(city)
        forecasts = []
        current_date = timezone.now().date()
        
        for day_offset in range(days):
            forecast_date = current_date + timedelta(days=day_offset)
            
            # Add some variation day by day
            temp_base = baseline['temp'] + random.uniform(-5, 5)
            temp_max = temp_base + random.uniform(3, 8)
            temp_min = temp_base - random.uniform(3, 8)
            temp_avg = (temp_max + temp_min) / 2
            
            humidity_avg = baseline['humidity'] + random.uniform(-15, 15)
            humidity_avg = max(30, min(100, humidity_avg))
            
            wind_avg = baseline['wind'] + random.uniform(-2, 3)
            wind_avg = max(0, wind_avg)
            
            # Weather condition
            if humidity_avg > 75:
                condition = random.choice([cls.WEATHER_CONDITIONS[4], cls.WEATHER_CONDITIONS[5]])
            elif humidity_avg < 50:
                condition = random.choice([cls.WEATHER_CONDITIONS[0], cls.WEATHER_CONDITIONS[1]])
            else:
                condition = random.choice(cls.WEATHER_CONDITIONS)
            
            rain_volume = random.uniform(0, 10) if humidity_avg > 70 else 0
            rain_probability = int(humidity_avg - 20) if humidity_avg > 70 else random.randint(0, 30)
            
            forecasts.append({
                'date': forecast_date.isoformat(),
                'temperature_max': round(temp_max, 1),
                'temperature_min': round(temp_min, 1),
                'temperature_avg': round(temp_avg, 1),
                'humidity_avg': round(humidity_avg, 1),
                'wind_speed_avg': round(wind_avg, 1),
                'description': condition['description'],
                'icon': condition['icon'],
                'rain_probability': rain_probability,
                'rain_volume': round(rain_volume, 2) if rain_volume > 0 else 0,
            })
        
        return forecasts
    
    @classmethod
    def get_historical_data(cls, city, days=30):
        """
        Generate mock historical weather data for analytics.
        
        Args:
            city: City name
            days: Number of days of historical data
            
        Returns:
            List of historical weather data dicts
        """
        baseline = cls._get_city_baseline(city)
        historical = []
        current_date = timezone.now().date()
        
        for day_offset in range(days, 0, -1):
            date = current_date - timedelta(days=day_offset)
            
            # Add seasonal variation
            day_of_year = date.timetuple().tm_yday
            seasonal_temp = baseline['temp'] + 10 * math.sin((day_of_year - 80) * 2 * math.pi / 365)
            
            # Daily variation
            temp = seasonal_temp + random.uniform(-5, 5)
            humidity = baseline['humidity'] + random.uniform(-15, 15)
            humidity = max(30, min(100, humidity))
            
            wind = baseline['wind'] + random.uniform(-2, 3)
            wind = max(0, wind)
            
            rain = random.uniform(0, 8) if humidity > 70 else 0
            
            historical.append({
                'date': date.isoformat(),
                'temperature': round(temp, 1),
                'humidity': int(humidity),
                'wind_speed': round(wind, 1),
                'rain_volume': round(rain, 2) if rain > 0 else 0,
            })
        
        return historical

