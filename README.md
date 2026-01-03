# Weather & Data Analytics Dashboard

A full-stack Django application for real-time weather data visualization and historical weather analytics.

## Features

- **Real-time Weather Data**: Fetch current weather conditions using OpenWeatherMap API
- **7-Day Forecast**: View extended weather forecasts
- **Historical Data Storage**: Automatically stores weather data in the database
- **Data Analytics**: 
  - Temperature trends analysis
  - Humidity trends analysis
  - Rainfall analysis
  - Wind speed analysis
  - Multi-metric comparison charts
- **Modern UI**: Clean, responsive Bootstrap-based interface
- **Interactive Charts**: Chart.js visualizations for data trends
- **REST API**: REST-style API endpoints for all weather and analytics data

## Requirements

- Python 3.8+
- Django 4.2+
- OpenWeatherMap API Key (free tier available)

## Installation

1. **Clone or navigate to the project directory**

2. **Create a virtual environment** (recommended):
```bash
python -m venv venv
```

3. **Activate the virtual environment**:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

5. **Set up the database**:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create a superuser** (optional, for admin access):
```bash
python manage.py createsuperuser
```

7. **Configure OpenWeatherMap API Key**:
   
   Get your free API key from [OpenWeatherMap](https://openweathermap.org/api)
   
   Then set it in one of these ways:
   
   **Option 1: Environment Variable** (Recommended)
   ```bash
   # Windows PowerShell
   $env:OPENWEATHER_API_KEY="your-api-key-here"
   
   # Windows CMD
   set OPENWEATHER_API_KEY=your-api-key-here
   
   # Linux/Mac
   export OPENWEATHER_API_KEY=your-api-key-here
   ```
   
   **Option 2: Edit settings.py**
   ```python
   OPENWEATHER_API_KEY = 'your-api-key-here'
   ```

8. **Run the development server**:
```bash
python manage.py runserver
```

9. **Access the application**:
   - Dashboard: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Usage

1. **Search for Weather**:
   - Enter a city name in the search box
   - Click "Search" or press Enter
   - View current weather conditions and forecast

2. **View Analytics**:
   - After searching for a city, analytics charts will automatically load
   - View temperature, humidity, rainfall, and wind trends
   - Compare multiple metrics in the comparison chart

3. **API Endpoints**:
   - `GET /api/weather/current/?city=London` - Current weather
   - `GET /api/weather/forecast/?city=London&days=7` - Weather forecast
   - `GET /api/analytics/temperature/?city=London&days=30` - Temperature trends
   - `GET /api/analytics/humidity/?city=London&days=30` - Humidity trends
   - `GET /api/analytics/rainfall/?city=London&days=30` - Rainfall analysis
   - `GET /api/analytics/wind/?city=London&days=30` - Wind speed analysis
   - `GET /api/analytics/comparison/?city=London&days=7` - Multi-metric comparison

## Project Structure

```
weather_dashboard/
├── manage.py
├── requirements.txt
├── README.md
├── weather_dashboard/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── weather/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── services.py      # OpenWeatherMap API integration
│   └── analytics.py    # Data analytics with Pandas
├── templates/
│   └── weather/
│       └── dashboard.html
└── static/             # Static files (if any)
```

## Technologies Used

- **Backend**: Django 4.2
- **Database**: SQLite (default, can be changed to PostgreSQL/MySQL)
- **Data Processing**: Pandas
- **API Integration**: OpenWeatherMap API
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Charts**: Chart.js
- **Icons**: Bootstrap Icons

## Database Models

- **WeatherData**: Stores historical current weather data
- **ForecastData**: Stores forecast data for future reference

## Best Practices

- Follows Django best practices (MVC pattern)
- REST-style API endpoints
- Service layer for API integration
- Analytics module separated from views
- Clean, commented, production-ready code
- Error handling for API failures
- Responsive design for mobile devices

## Notes

- The free tier of OpenWeatherMap API has rate limits
- Historical data is stored automatically when fetching current weather
- Analytics require historical data to be meaningful (data accumulates over time)
- For production, change `DEBUG = False` in settings.py and set a proper `SECRET_KEY`

## License

This project is open source and available for educational purposes.

