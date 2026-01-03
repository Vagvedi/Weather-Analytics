"""
Weather service for interacting with OpenWeatherMap API.
Falls back to mock data when external API is unavailable.
"""
import requests
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from .models import WeatherData, ForecastData
from .mock_data import MockWeatherData
import logging

logger = logging.getLogger(__name__)


class WeatherService:
    """
    Service class for fetching and storing weather data from OpenWeatherMap API.
    """
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key=None):
        self.api_key = api_key or settings.OPENWEATHER_API_KEY
    
    def _make_request(self, endpoint, params):
        """
        Make HTTP request to OpenWeatherMap API.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters dict
            
        Returns:
            Tuple of (response_data, error_code, error_message)
            - If success: (dict, None, None)
            - If city not found: (None, 404, "City not found")
            - If API unavailable: (None, 503, "Weather service temporarily unavailable")
            - If invalid API key: (None, 503, "Weather service temporarily unavailable")
        """
        url = f"{self.BASE_URL}/{endpoint}"
        params['appid'] = self.api_key
        params['units'] = 'metric'  # Use Celsius
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            # Handle specific HTTP status codes
            if response.status_code == 404:
                logger.warning(f"City not found: {params.get('q', 'unknown')}")
                return (None, 404, "City not found")
            
            if response.status_code == 401:
                logger.error("Invalid API key")
                return (None, 503, "Weather service temporarily unavailable")
            
            if response.status_code != 200:
                logger.error(f"API returned status {response.status_code}")
                return (None, 503, "Weather service temporarily unavailable")
            
            # Parse JSON response
            data = response.json()
            
            # Validate response structure for current weather
            if endpoint == 'weather':
                if 'cod' in data and data['cod'] == '404':
                    return (None, 404, "City not found")
                
                # Validate required fields exist
                required_fields = ['name', 'main', 'sys', 'weather']
                for field in required_fields:
                    if field not in data:
                        logger.error(f"Invalid API response: missing field '{field}'")
                        return (None, 503, "Weather service temporarily unavailable")
                
                # Validate nested fields
                if 'temp' not in data['main']:
                    logger.error("Invalid API response: missing 'main.temp'")
                    return (None, 503, "Weather service temporarily unavailable")
                
                if not data['weather'] or 'description' not in data['weather'][0]:
                    logger.error("Invalid API response: missing weather description")
                    return (None, 503, "Weather service temporarily unavailable")
            
            # Validate response structure for forecast
            if endpoint == 'forecast':
                if 'cod' in data and data['cod'] == '404':
                    return (None, 404, "City not found")
                
                if 'list' not in data or 'city' not in data:
                    logger.error("Invalid forecast API response")
                    return (None, 503, "Weather service temporarily unavailable")
            
            return (data, None, None)
            
        except requests.exceptions.Timeout:
            logger.error("API request timeout")
            return (None, 503, "Weather service temporarily unavailable")
        except requests.exceptions.ConnectionError:
            logger.error("API connection error")
            return (None, 503, "Weather service temporarily unavailable")
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API request failed: {e}")
            return (None, 503, "Weather service temporarily unavailable")
        except (ValueError, KeyError) as e:
            logger.error(f"Invalid API response format: {e}")
            return (None, 503, "Weather service temporarily unavailable")
    
    def get_current_weather(self, city, country_code=None, use_mock=False):
        """
        Fetch current weather data for a city.
        NEVER uses mock data for invalid cities - only for testing when explicitly requested.
        
        Args:
            city: City name
            country_code: Optional country code (e.g., 'US', 'GB')
            use_mock: Force use of mock data (for testing only)
            
        Returns:
            Tuple of (weather_data_dict, error_code, error_message)
            - If success: (dict, None, None)
            - If city not found: (None, 404, "City not found")
            - If service unavailable: (None, 503, "Weather service temporarily unavailable")
        """
        # Only use mock data if explicitly requested for testing
        if use_mock:
            logger.info(f"Using mock data for {city} (testing mode)")
            return (MockWeatherData.get_current_weather(city, country_code), None, None)
        
        # Validate API key exists
        if not self.api_key or self.api_key == 'your-api-key-here':
            logger.warning("API key not configured")
            return (None, 503, "Weather service temporarily unavailable")
        
        query = f"{city},{country_code}" if country_code else city
        params = {'q': query}
        
        data, error_code, error_message = self._make_request('weather', params)
        
        # If request failed, return error (never use mock data for invalid cities)
        if error_code:
            return (None, error_code, error_message)
        
        # Validate data structure before processing
        try:
            # Store in database only if data is valid
            try:
                weather_data = self._save_current_weather(data)
            except Exception as e:
                logger.error(f"Error saving weather data: {e}")
                # Continue even if save fails
            
            # API timestamps are in UTC, convert to timezone-aware
            dt = datetime.utcfromtimestamp(data['dt'])
            dt_aware = timezone.make_aware(dt) if timezone.is_naive(dt) else dt
            
            return ({
                'city': data['name'],
                'country': data['sys'].get('country', ''),
                'temperature': data['main']['temp'],
                'feels_like': data['main'].get('feels_like'),
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind'].get('speed', 0),
                'wind_direction': data['wind'].get('deg'),
                'visibility': data.get('visibility'),
                'cloudiness': data['clouds'].get('all', 0),
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'rain_volume': data.get('rain', {}).get('3h'),
                'snow_volume': data.get('snow', {}).get('3h'),
                'timestamp': dt_aware.isoformat(),
            }, None, None)
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Invalid data structure: {e}")
            return (None, 503, "Weather service temporarily unavailable")
    
    def get_forecast(self, city, country_code=None, days=7, use_mock=False):
        """
        Fetch weather forecast for a city.
        NEVER uses mock data for invalid cities - only for testing when explicitly requested.
        
        Args:
            city: City name
            country_code: Optional country code
            days: Number of days to forecast (max 5 for free API)
            use_mock: Force use of mock data (for testing only)
            
        Returns:
            Tuple of (forecast_data_list, error_code, error_message)
            - If success: (list, None, None)
            - If city not found: (None, 404, "City not found")
            - If service unavailable: (None, 503, "Weather service temporarily unavailable")
        """
        # Only use mock data if explicitly requested for testing
        if use_mock:
            logger.info(f"Using mock forecast data for {city} (testing mode)")
            return (MockWeatherData.get_forecast(city, country_code, days), None, None)
        
        # Validate API key exists
        if not self.api_key or self.api_key == 'your-api-key-here':
            logger.warning("API key not configured")
            return (None, 503, "Weather service temporarily unavailable")
        
        query = f"{city},{country_code}" if country_code else city
        params = {'q': query, 'cnt': min(days * 8, 40)}  # 8 forecasts per day, max 40
        
        data, error_code, error_message = self._make_request('forecast', params)
        
        # If request failed, return error (never use mock data for invalid cities)
        if error_code:
            return (None, error_code, error_message)
        
        # Validate and process forecast data
        try:
            forecasts = []
            current_date = timezone.now().date()
            city_name = data.get('city', {}).get('name', city)
            city_country = data.get('city', {}).get('country', '')
            
            for item in data.get('list', []):
                # Validate item structure
                if 'main' not in item or 'weather' not in item or not item['weather']:
                    continue
                
                # API timestamps are in UTC, convert to timezone-aware
                dt = datetime.utcfromtimestamp(item['dt'])
                forecast_time = timezone.make_aware(dt) if timezone.is_naive(dt) else dt
                forecast_date = forecast_time.date()
                
                # Only include future forecasts
                if forecast_date >= current_date:
                    forecast_data = {
                        'date': forecast_date.isoformat(),
                        'time': forecast_time.isoformat(),
                        'temperature': item['main']['temp'],
                        'feels_like': item['main'].get('feels_like'),
                        'humidity': item['main']['humidity'],
                        'pressure': item['main']['pressure'],
                        'wind_speed': item['wind'].get('speed', 0),
                        'description': item['weather'][0]['description'],
                        'icon': item['weather'][0]['icon'],
                        'rain_probability': item.get('pop', 0) * 100,  # Convert to percentage
                        'rain_volume': item.get('rain', {}).get('3h'),
                    }
                    forecasts.append((forecast_data, forecast_time))
                    
                    # Store in database
                    try:
                        self._save_forecast(
                            {'name': city_name, 'country': city_country}, 
                            forecast_data, 
                            forecast_time
                        )
                    except Exception as e:
                        logger.error(f"Error saving forecast: {e}")
            
            # Extract just the forecast data for grouping
            forecast_data_list = [fd for fd, _ in forecasts]
            
            # Group by day and return daily forecasts
            daily_forecasts = self._group_forecasts_by_day(forecast_data_list)
            return (daily_forecasts[:days], None, None)
        except (KeyError, TypeError, ValueError) as e:
            logger.error(f"Invalid forecast data structure: {e}")
            return (None, 503, "Weather service temporarily unavailable")
    
    def _group_forecasts_by_day(self, forecasts):
        """
        Group hourly forecasts into daily forecasts.
        """
        daily = {}
        for forecast in forecasts:
            date = forecast['date']
            if date not in daily:
                daily[date] = {
                    'date': date,
                    'temperatures': [],
                    'humidity': [],
                    'wind_speed': [],
                    'descriptions': [],
                    'icons': [],
                    'rain_probability': [],
                    'rain_volume': [],
                }
            
            daily[date]['temperatures'].append(forecast['temperature'])
            daily[date]['humidity'].append(forecast['humidity'])
            daily[date]['wind_speed'].append(forecast['wind_speed'])
            daily[date]['descriptions'].append(forecast['description'])
            daily[date]['icons'].append(forecast['icon'])
            daily[date]['rain_probability'].append(forecast['rain_probability'])
            if forecast.get('rain_volume'):
                daily[date]['rain_volume'].append(forecast['rain_volume'])
        
        # Calculate daily averages/max
        result = []
        for date, data in sorted(daily.items()):
            result.append({
                'date': date,
                'temperature_max': max(data['temperatures']),
                'temperature_min': min(data['temperatures']),
                'temperature_avg': sum(data['temperatures']) / len(data['temperatures']),
                'humidity_avg': sum(data['humidity']) / len(data['humidity']),
                'wind_speed_avg': sum(data['wind_speed']) / len(data['wind_speed']),
                'description': max(set(data['descriptions']), key=data['descriptions'].count),  # Most common
                'icon': max(set(data['icons']), key=data['icons'].count),  # Most common
                'rain_probability': max(data['rain_probability']),
                'rain_volume': sum(data['rain_volume']) if data['rain_volume'] else 0,
            })
        
        return result
    
    def _save_current_weather(self, api_data):
        """
        Save current weather data to database.
        """
        try:
            weather_data = WeatherData.objects.create(
                city=api_data['name'],
                country=api_data['sys'].get('country', ''),
                temperature=api_data['main']['temp'],
                feels_like=api_data['main'].get('feels_like'),
                humidity=api_data['main']['humidity'],
                pressure=api_data['main']['pressure'],
                wind_speed=api_data['wind'].get('speed', 0),
                wind_direction=api_data['wind'].get('deg'),
                visibility=api_data.get('visibility'),
                cloudiness=api_data['clouds'].get('all', 0),
                description=api_data['weather'][0]['description'],
                icon=api_data['weather'][0]['icon'],
                rain_volume=api_data.get('rain', {}).get('3h'),
                snow_volume=api_data.get('snow', {}).get('3h'),
                # API timestamps are in UTC, convert to timezone-aware
                dt = datetime.utcfromtimestamp(api_data['dt']),
                dt_aware = timezone.make_aware(dt) if timezone.is_naive(dt) else dt,
                timestamp=dt_aware,
                date=dt_aware.date(),
            )
            return weather_data
        except Exception as e:
            logger.error(f"Error saving weather data: {e}")
            return None
    
    def _save_forecast(self, city_info, forecast_data, forecast_time):
        """
        Save forecast data to database.
        """
        try:
            ForecastData.objects.create(
                city=city_info['name'],
                country=city_info.get('country', ''),
                forecast_date=forecast_time,
                temperature=forecast_data['temperature'],
                feels_like=forecast_data.get('feels_like'),
                humidity=forecast_data['humidity'],
                pressure=forecast_data['pressure'],
                wind_speed=forecast_data['wind_speed'],
                description=forecast_data['description'],
                icon=forecast_data['icon'],
                rain_probability=forecast_data.get('rain_probability'),
            )
        except Exception as e:
            logger.error(f"Error saving forecast data: {e}")

