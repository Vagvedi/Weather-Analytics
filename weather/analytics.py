"""
Data analytics module for weather data using Pandas.
Falls back to mock data when database is empty.
"""
import pandas as pd
import numpy as np
from django.utils import timezone
from datetime import timedelta
from .models import WeatherData
from .mock_data import MockWeatherData
import logging

logger = logging.getLogger(__name__)


def to_json_safe(value):
    """
    Convert numpy/pandas types to JSON-serializable Python native types.
    
    Args:
        value: Any value that might be numpy/pandas type
        
    Returns:
        JSON-serializable Python native type
    """
    if pd.isna(value):
        return None
    elif isinstance(value, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(value)
    elif isinstance(value, (np.floating, np.float64, np.float32, np.float16)):
        return float(value)
    elif isinstance(value, (np.bool_, np.bool8)):
        return bool(value)
    elif isinstance(value, pd.Series):
        return [to_json_safe(v) for v in value.tolist()]
    elif isinstance(value, pd.DataFrame):
        return value.to_dict('records')
    elif isinstance(value, (list, tuple)):
        return [to_json_safe(v) for v in value]
    elif isinstance(value, dict):
        return {k: to_json_safe(v) for k, v in value.items()}
    elif isinstance(value, (pd.Timestamp, pd.DatetimeTZDtype)):
        return value.isoformat() if hasattr(value, 'isoformat') else str(value)
    else:
        return value


class WeatherAnalytics:
    """
    Class for performing analytics on weather data.
    """
    
    def __init__(self, city=None):
        """
        Initialize analytics for a specific city or all cities.
        
        Args:
            city: Optional city name to filter data
        """
        self.city = city
    
    def get_dataframe(self, days=30, use_mock=False):
        """
        Get weather data as pandas DataFrame.
        Falls back to mock data if database is empty.
        
        Args:
            days: Number of days of historical data to retrieve
            use_mock: Force use of mock data (for testing)
            
        Returns:
            pandas DataFrame
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        queryset = WeatherData.objects.filter(timestamp__gte=start_date)
        if self.city:
            queryset = queryset.filter(city__iexact=self.city)
        
        data = list(queryset.values(
            'city', 'temperature', 'humidity', 'pressure', 
            'wind_speed', 'rain_volume', 'snow_volume', 
            'cloudiness', 'timestamp', 'date'
        ))
        
        # Fallback to mock data if database is empty
        if not data or use_mock:
            if not use_mock:
                logger.info(f"No database data found, using mock data for analytics")
            
            city = self.city or 'Default'
            mock_data = MockWeatherData.get_historical_data(city, days)
            
            # Convert mock data to DataFrame format
            df_data = []
            for item in mock_data:
                df_data.append({
                    'city': city,
                    'temperature': item['temperature'],
                    'humidity': item['humidity'],
                    'pressure': 1013,  # Default pressure
                    'wind_speed': item['wind_speed'],
                    'rain_volume': item['rain_volume'],
                    'snow_volume': 0,
                    'cloudiness': 50,
                    'timestamp': pd.Timestamp(item['date']),
                    'date': pd.Timestamp(item['date']).date(),
                })
            
            df = pd.DataFrame(df_data)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['date'] = pd.to_datetime(df['date'])
            return df
        
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def get_temperature_trends(self, days=30, use_mock=False):
        """
        Analyze temperature trends over time.
        
        Returns:
            Dict with trend data for charts (all values JSON-serializable)
        """
        try:
            df = self.get_dataframe(days, use_mock=use_mock)
            if df.empty:
                return {
                    'dates': [],
                    'temperatures': [],
                    'min_temperatures': [],
                    'max_temperatures': [],
                    'avg_temperature': 0.0,
                    'min_temperature': 0.0,
                    'max_temperature': 0.0,
                    'trend': 'stable',
                }
            
            # Group by date and calculate daily averages
            daily = df.groupby('date').agg({
                'temperature': ['mean', 'min', 'max'],
            }).reset_index()
            
            daily.columns = ['date', 'avg_temp', 'min_temp', 'max_temp']
            daily = daily.sort_values('date')
            
            # Calculate trend (increasing, decreasing, stable)
            if len(daily) > 1:
                first_half = float(daily['avg_temp'].iloc[:len(daily)//2].mean())
                second_half = float(daily['avg_temp'].iloc[len(daily)//2:].mean())
                diff = second_half - first_half
                
                if diff > 1:
                    trend = 'increasing'
                elif diff < -1:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            # Convert all values to JSON-safe types
            result = {
                'dates': [str(d) for d in daily['date'].dt.strftime('%Y-%m-%d')],
                'temperatures': [to_json_safe(float(v)) for v in daily['avg_temp'].round(2)],
                'min_temperatures': [to_json_safe(float(v)) for v in daily['min_temp'].round(2)],
                'max_temperatures': [to_json_safe(float(v)) for v in daily['max_temp'].round(2)],
                'avg_temperature': to_json_safe(float(df['temperature'].mean())),
                'min_temperature': to_json_safe(float(df['temperature'].min())),
                'max_temperature': to_json_safe(float(df['temperature'].max())),
                'trend': trend,
            }
            
            return result
        except Exception as e:
            logger.error(f"Error in get_temperature_trends: {e}")
            return {
                'dates': [],
                'temperatures': [],
                'min_temperatures': [],
                'max_temperatures': [],
                'avg_temperature': 0.0,
                'min_temperature': 0.0,
                'max_temperature': 0.0,
                'trend': 'stable',
            }
    
    def get_humidity_trends(self, days=30, use_mock=False):
        """
        Analyze humidity trends over time.
        
        Returns:
            Dict with humidity trend data (all values JSON-serializable)
        """
        try:
            df = self.get_dataframe(days, use_mock=use_mock)
            if df.empty:
                return {
                    'dates': [],
                    'humidity': [],
                    'min_humidity': [],
                    'max_humidity': [],
                    'avg_humidity': 0.0,
                    'min_humidity': 0,
                    'max_humidity': 0,
                }
            
            daily = df.groupby('date')['humidity'].agg(['mean', 'min', 'max']).reset_index()
            daily.columns = ['date', 'avg_humidity', 'min_humidity', 'max_humidity']
            daily = daily.sort_values('date')
            
            # Convert all values to JSON-safe types
            result = {
                'dates': [str(d) for d in daily['date'].dt.strftime('%Y-%m-%d')],
                'humidity': [to_json_safe(float(v)) for v in daily['avg_humidity'].round(2)],
                'min_humidity': [to_json_safe(int(v)) for v in daily['min_humidity']],
                'max_humidity': [to_json_safe(int(v)) for v in daily['max_humidity']],
                'avg_humidity': to_json_safe(float(df['humidity'].mean())),
                'min_humidity': to_json_safe(int(df['humidity'].min())),
                'max_humidity': to_json_safe(int(df['humidity'].max())),
            }
            
            return result
        except Exception as e:
            logger.error(f"Error in get_humidity_trends: {e}")
            return {
                'dates': [],
                'humidity': [],
                'min_humidity': [],
                'max_humidity': [],
                'avg_humidity': 0.0,
                'min_humidity': 0,
                'max_humidity': 0,
            }
    
    def get_rainfall_analysis(self, days=30, use_mock=False):
        """
        Analyze rainfall data.
        
        Returns:
            Dict with rainfall analysis (all values JSON-serializable)
        """
        try:
            df = self.get_dataframe(days, use_mock=use_mock)
            if df.empty:
                return {
                    'dates': [],
                    'rainfall': [],
                    'total_rainfall': 0.0,
                    'rainy_days': 0,
                    'avg_rainfall': 0.0,
                }
            
            # Fill NaN with 0 for days without rain
            df['rain_volume'] = df['rain_volume'].fillna(0.0)
            
            daily = df.groupby('date')['rain_volume'].sum().reset_index()
            daily.columns = ['date', 'rainfall']
            daily = daily.sort_values('date')
            
            rainy_days = int((daily['rainfall'] > 0).sum())
            total_rainfall = float(daily['rainfall'].sum())
            avg_rainfall = float(total_rainfall / len(daily)) if len(daily) > 0 else 0.0
            
            # Convert all values to JSON-safe types
            result = {
                'dates': [str(d) for d in daily['date'].dt.strftime('%Y-%m-%d')],
                'rainfall': [to_json_safe(float(v)) for v in daily['rainfall'].round(2)],
                'total_rainfall': to_json_safe(round(total_rainfall, 2)),
                'rainy_days': to_json_safe(rainy_days),
                'avg_rainfall': to_json_safe(round(avg_rainfall, 2)),
            }
            
            return result
        except Exception as e:
            logger.error(f"Error in get_rainfall_analysis: {e}")
            return {
                'dates': [],
                'rainfall': [],
                'total_rainfall': 0.0,
                'rainy_days': 0,
                'avg_rainfall': 0.0,
            }
    
    def get_wind_analysis(self, days=30, use_mock=False):
        """
        Analyze wind speed data.
        
        Returns:
            Dict with wind analysis (all values JSON-serializable)
        """
        try:
            df = self.get_dataframe(days, use_mock=use_mock)
            if df.empty:
                return {
                    'dates': [],
                    'wind_speed': [],
                    'avg_wind_speed': 0.0,
                    'max_wind_speed': 0.0,
                }
            
            daily = df.groupby('date')['wind_speed'].mean().reset_index()
            daily = daily.sort_values('date')
            
            # Convert all values to JSON-safe types
            result = {
                'dates': [str(d) for d in daily['date'].dt.strftime('%Y-%m-%d')],
                'wind_speed': [to_json_safe(float(v)) for v in daily['wind_speed'].round(2)],
                'avg_wind_speed': to_json_safe(round(float(df['wind_speed'].mean()), 2)),
                'max_wind_speed': to_json_safe(round(float(df['wind_speed'].max()), 2)),
            }
            
            return result
        except Exception as e:
            logger.error(f"Error in get_wind_analysis: {e}")
            return {
                'dates': [],
                'wind_speed': [],
                'avg_wind_speed': 0.0,
                'max_wind_speed': 0.0,
            }
    
    def get_comparison_data(self, days=7, use_mock=False):
        """
        Get comparison data for multiple metrics.
        
        Returns:
            Dict with comparison data for bar charts (all values JSON-serializable)
        """
        try:
            df = self.get_dataframe(days, use_mock=use_mock)
            if df.empty:
                return {
                    'dates': [],
                    'temperature': [],
                    'humidity': [],
                    'wind_speed': [],
                }
            
            daily = df.groupby('date').agg({
                'temperature': 'mean',
                'humidity': 'mean',
                'wind_speed': 'mean',
            }).reset_index()
            daily = daily.sort_values('date')
            
            # Convert all values to JSON-safe types
            result = {
                'dates': [str(d) for d in daily['date'].dt.strftime('%m-%d')],
                'temperature': [to_json_safe(float(v)) for v in daily['temperature'].round(2)],
                'humidity': [to_json_safe(float(v)) for v in daily['humidity'].round(2)],
                'wind_speed': [to_json_safe(float(v)) for v in daily['wind_speed'].round(2)],
            }
            
            return result
        except Exception as e:
            logger.error(f"Error in get_comparison_data: {e}")
            return {
                'dates': [],
                'temperature': [],
                'humidity': [],
                'wind_speed': [],
            }

