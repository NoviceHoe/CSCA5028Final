from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import pytz
from datetime import datetime
from app import app, db, User, fetch_max_daily_temperature

# Function to send email
def send_email(to_email, subject, message):
    # Set up your email server (use your own credentials)
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'your_email@gmail.com'  # Replace with your email
    smtp_password = 'your_password'     # Replace with your password

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    # Send the email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

# Function to calculate and notify users daily
def calculate_and_notify_users():
    with app.app_context():
        users = User.query.all()
        for user in users:
            # Fetch max daily temperature for the user's coordinates
            max_temp = fetch_max_daily_temperature(user.latitude, user.longitude)

            if max_temp is not None:
                max_temp_f = (max_temp * (9 / 5) + 32)

                # Calculate the result based on the max temperature and user's weight
                if max_temp_f > 70:
                    result = user.weight + ((max_temp_f - 70) * 2)
                else:
                    result = user.weight

                # Update the user's max_daily_temp in the database
                user.max_daily_temp = max_temp
                db.session.commit()

                # Email the result to the user
                subject = "Your Daily Temperature and Weight Result"
                message = (f"Hello,\n\nBased on today's maximum temperature of {max_temp_f}°F at your location, "
                           f"your calculated result is {result}.\n\nRegards,\nDaily Temperature App")
                send_email(user.email, subject, message)

# Schedule the task to run daily at midnight
def schedule_daily_task():
    scheduler = BackgroundScheduler(timezone=pytz.utc)
    scheduler.add_job(calculate_and_notify_users, trigger='cron', hour=0, minute=0)
    scheduler.start()

# Initialize and schedule the task
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    schedule_daily_task()
    app.run(debug=True)
