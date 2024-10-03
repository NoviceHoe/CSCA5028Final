from flask import Flask, render_template, request
from models import db, User
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import subprocess

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Function to initialize the database
def init_db():
    with app.app_context():
        db.create_all()  # Create database tables
        print("Database initialized and tables created.")

with app.app_context():
    init_db()

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Function to fetch maximum daily temperature for a user
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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        weight = float(request.form['weight'])
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        receive_daily_email = 'daily_email' in request.form

        # Create and save the new user in the database
        new_user = User(weight=weight, latitude=latitude, longitude=longitude)
        db.session.add(new_user)
        db.session.commit()

        # Fetch the maximum daily temperature
        max_temp = fetch_max_daily_temperature(latitude, longitude)
        max_temp_f = ((max_temp * (9 / 5) + 32)) if max_temp is not None else None

        if max_temp_f is not None:
            # Calculate the result: weight * max daily temperature
            if max_temp_f > 70:
                result = weight + ((max_temp_f - 70) * 2)
            else:
                result = weight

            # Update the user's max_daily_temp in the database
            new_user.max_daily_temp = max_temp
            db.session.commit()  # Commit the updated user with max daily temp

            # Schedule the daily email task if the checkbox is checked
            if receive_daily_email:
                new_user.receive_daily_email = True
                db.session.commit()

                # Start daily email task subprocess (not recommended for production, consider alternative scheduling)
                subprocess.Popen(['python', 'daily_email_task.py'])

            # Pass the result to the next page
            return render_template('result.html', result=result, weight=weight, max_temp=max_temp_f)
        else:
            return "Weather data could not be retrieved. Please try again later."
    
    return render_template('index.html')

# Ensure the application is running with the `flask run` command
if __name__ == '__main__':
    app.run(debug=True)
