"""
Views for weather dashboard application.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import logging

from .services import WeatherService
from .analytics import WeatherAnalytics

logger = logging.getLogger(__name__)


# =========================
# DASHBOARD VIEW
# =========================

def dashboard(request):
    """
    Main dashboard page.
    """
    return render(request, 'weather/dashboard.html')


# =========================
# WEATHER APIs
# =========================

@require_http_methods(["GET"])
def api_current_weather(request):
    """
    REST API endpoint for current weather data.
    Returns proper HTTP status codes for different error scenarios.

    Query params:
        city: City name (required)
        country: Optional country code
    """
    city = request.GET.get('city', '').strip()
    country = request.GET.get('country')

    if not city:
        return JsonResponse(
            {"success": False, "error": "City parameter is required"},
            status=400
        )

    # Basic input validation
    if len(city) < 2:
        return JsonResponse(
            {"success": False, "error": "City name must be at least 2 characters"},
            status=400
        )

    service = WeatherService()
    weather_data, error_code, error_message = service.get_current_weather(city, country)

    # Handle errors with proper status codes
    if error_code:
        return JsonResponse(
            {"success": False, "error": error_message},
            status=error_code
        )

    return JsonResponse(
        {"success": True, "data": weather_data},
        status=200
    )


@require_http_methods(["GET"])
def api_forecast(request):
    """
    REST API endpoint for weather forecast.
    Returns proper HTTP status codes for different error scenarios.

    Query params:
        city: City name (required)
        country: Optional country code
        days: Number of days (default: 7)
    """
    city = request.GET.get('city', '').strip()
    country = request.GET.get('country')
    
    try:
        days = int(request.GET.get('days', 7))
        if days < 1 or days > 7:
            days = 7
    except (ValueError, TypeError):
        days = 7

    if not city:
        return JsonResponse(
            {"success": False, "error": "City parameter is required"},
            status=400
        )

    # Basic input validation
    if len(city) < 2:
        return JsonResponse(
            {"success": False, "error": "City name must be at least 2 characters"},
            status=400
        )

    service = WeatherService()
    forecast_data, error_code, error_message = service.get_forecast(city, country, days)

    # Handle errors with proper status codes
    if error_code:
        return JsonResponse(
            {"success": False, "error": error_message},
            status=error_code
        )

    return JsonResponse(
        {"success": True, "data": forecast_data},
        status=200
    )


# =========================
# ANALYTICS APIs
# =========================

@require_http_methods(["GET"])
def api_analytics_temperature(request):
    """
    Temperature trend analytics.
    Returns JSON-safe data, never crashes with 500.
    """
    try:
        city = request.GET.get('city')
        try:
            days = int(request.GET.get('days', 30))
            if days < 1 or days > 365:
                days = 30
        except (ValueError, TypeError):
            days = 30

        analytics = WeatherAnalytics(city=city)
        trend_data = analytics.get_temperature_trends(days)

        # Ensure data is JSON-serializable
        if not isinstance(trend_data, dict):
            trend_data = {}

        return JsonResponse(
            {"success": True, "data": trend_data},
            status=200
        )
    except Exception as e:
        logger.error(f"Error in api_analytics_temperature: {e}", exc_info=True)
        return JsonResponse(
            {
                "success": False,
                "error": "Failed to retrieve temperature analytics",
                "data": {
                    'dates': [],
                    'temperatures': [],
                    'min_temperatures': [],
                    'max_temperatures': [],
                    'avg_temperature': 0.0,
                    'min_temperature': 0.0,
                    'max_temperature': 0.0,
                    'trend': 'stable',
                }
            },
            status=200  # Return 200 with error flag to prevent frontend crashes
        )


@require_http_methods(["GET"])
def api_analytics_humidity(request):
    """
    Humidity trend analytics.
    Returns JSON-safe data, never crashes with 500.
    """
    try:
        city = request.GET.get('city')
        try:
            days = int(request.GET.get('days', 30))
            if days < 1 or days > 365:
                days = 30
        except (ValueError, TypeError):
            days = 30

        analytics = WeatherAnalytics(city=city)
        trend_data = analytics.get_humidity_trends(days)

        # Ensure data is JSON-serializable
        if not isinstance(trend_data, dict):
            trend_data = {}

        return JsonResponse(
            {"success": True, "data": trend_data},
            status=200
        )
    except Exception as e:
        logger.error(f"Error in api_analytics_humidity: {e}", exc_info=True)
        return JsonResponse(
            {
                "success": False,
                "error": "Failed to retrieve humidity analytics",
                "data": {
                    'dates': [],
                    'humidity': [],
                    'min_humidity': [],
                    'max_humidity': [],
                    'avg_humidity': 0.0,
                    'min_humidity': 0,
                    'max_humidity': 0,
                }
            },
            status=200
        )


@require_http_methods(["GET"])
def api_analytics_rainfall(request):
    """
    Rainfall analysis.
    Returns JSON-safe data, never crashes with 500.
    """
    try:
        city = request.GET.get('city')
        try:
            days = int(request.GET.get('days', 30))
            if days < 1 or days > 365:
                days = 30
        except (ValueError, TypeError):
            days = 30

        analytics = WeatherAnalytics(city=city)
        rainfall_data = analytics.get_rainfall_analysis(days)

        # Ensure data is JSON-serializable
        if not isinstance(rainfall_data, dict):
            rainfall_data = {}

        return JsonResponse(
            {"success": True, "data": rainfall_data},
            status=200
        )
    except Exception as e:
        logger.error(f"Error in api_analytics_rainfall: {e}", exc_info=True)
        return JsonResponse(
            {
                "success": False,
                "error": "Failed to retrieve rainfall analytics",
                "data": {
                    'dates': [],
                    'rainfall': [],
                    'total_rainfall': 0.0,
                    'rainy_days': 0,
                    'avg_rainfall': 0.0,
                }
            },
            status=200
        )


@require_http_methods(["GET"])
def api_analytics_wind(request):
    """
    Wind speed analysis.
    Returns JSON-safe data, never crashes with 500.
    """
    try:
        city = request.GET.get('city')
        try:
            days = int(request.GET.get('days', 30))
            if days < 1 or days > 365:
                days = 30
        except (ValueError, TypeError):
            days = 30

        analytics = WeatherAnalytics(city=city)
        wind_data = analytics.get_wind_analysis(days)

        # Ensure data is JSON-serializable
        if not isinstance(wind_data, dict):
            wind_data = {}

        return JsonResponse(
            {"success": True, "data": wind_data},
            status=200
        )
    except Exception as e:
        logger.error(f"Error in api_analytics_wind: {e}", exc_info=True)
        return JsonResponse(
            {
                "success": False,
                "error": "Failed to retrieve wind analytics",
                "data": {
                    'dates': [],
                    'wind_speed': [],
                    'avg_wind_speed': 0.0,
                    'max_wind_speed': 0.0,
                }
            },
            status=200
        )


@require_http_methods(["GET"])
def api_analytics_comparison(request):
    """
    Multi-metric comparison analytics.
    Returns JSON-safe data, never crashes with 500.
    """
    try:
        city = request.GET.get('city')
        try:
            days = int(request.GET.get('days', 7))
            if days < 1 or days > 365:
                days = 7
        except (ValueError, TypeError):
            days = 7

        analytics = WeatherAnalytics(city=city)
        comparison_data = analytics.get_comparison_data(days)

        # Ensure data is JSON-serializable
        if not isinstance(comparison_data, dict):
            comparison_data = {}

        return JsonResponse(
            {"success": True, "data": comparison_data},
            status=200
        )
    except Exception as e:
        logger.error(f"Error in api_analytics_comparison: {e}", exc_info=True)
        return JsonResponse(
            {
                "success": False,
                "error": "Failed to retrieve comparison analytics",
                "data": {
                    'dates': [],
                    'temperature': [],
                    'humidity': [],
                    'wind_speed': [],
                }
            },
            status=200
        )
