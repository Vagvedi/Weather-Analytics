# Quick Setup Guide

## Step-by-Step Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up the database**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Get OpenWeatherMap API Key**:
   - Visit https://openweathermap.org/api
   - Sign up for a free account
   - Get your API key from the dashboard

4. **Set the API Key**:
   
   **Windows PowerShell**:
   ```powershell
   $env:OPENWEATHER_API_KEY="your-api-key-here"
   ```
   
   **Windows CMD**:
   ```cmd
   set OPENWEATHER_API_KEY=your-api-key-here
   ```
   
   **Linux/Mac**:
   ```bash
   export OPENWEATHER_API_KEY=your-api-key-here
   ```
   
   Or edit `weather_dashboard/settings.py` and replace:
   ```python
   OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', 'your-api-key-here')
   ```
   with:
   ```python
   OPENWEATHER_API_KEY = 'your-actual-api-key-here'
   ```

5. **Run the server**:
   ```bash
   python manage.py runserver
   ```

6. **Open your browser**:
   - Navigate to http://127.0.0.1:8000/
   - Search for any city to see weather data and analytics

## Testing the API

You can test the API endpoints directly:

```bash
# Current weather
curl "http://127.0.0.1:8000/api/weather/current/?city=London"

# Forecast
curl "http://127.0.0.1:8000/api/weather/forecast/?city=London&days=7"

# Analytics (requires historical data)
curl "http://127.0.0.1:8000/api/analytics/temperature/?city=London&days=30"
```

## Notes

- Historical data accumulates over time as you search for cities
- Analytics charts will show more meaningful data after multiple searches
- The free OpenWeatherMap API has rate limits (60 calls/minute)

