import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from models import db, User
from app import app

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def fetch_max_daily_temperature(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max",
        "forecast_days": 1
    }

    # Make the API call
    responses = openmeteo.weather_api(url, params=params)

    # Process the response and return the maximum temperature
    if responses:
        response = responses[0]
        daily = response.Daily()
        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
        
        if daily_temperature_2m_max.size > 0:
            return daily_temperature_2m_max[0]  # Return the first value
    return None
    print(daily_temperature_2m_max[0])
