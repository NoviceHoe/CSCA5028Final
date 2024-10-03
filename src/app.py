import sqlite3
from flask import Flask, request, g

app = Flask(__name__)

# Specify the path to the database
DATABASE = './user_data.db'

def get_db():
    """Connect to the SQLite database."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close the database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database by creating the table if it doesn't exist."""
    with app.app_context():  # Ensure we're in the Flask app context
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weight REAL,
                lat REAL,
                lon REAL,
                max_temp REAL
            )
            ''')
            db.commit()
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Error initializing the database: {e}")

@app.route("/")
def main():
    """Render the main page with the form."""
    return '''
     <form action="/echo_user_input" method="POST">
         <label>Enter your weight (lbs):</label>
         <input name="user_weight" type="text">
         <br>
         <label>Enter your latitude:</label>
         <input name="user_lat" type="text">
         <br>
         <label>Enter your longitude:</label>
         <input name="user_lon" type="text">
         <br>
         <input type="submit" value="Submit!">
     </form>
     '''

@app.route("/echo_user_input", methods=["POST"])
def echo_input():
    """Handle the form submission and store the input in the database."""
    # Get user inputs
    input_weight = request.form.get("user_weight", "")
    input_lat = request.form.get("user_lat", "")
    input_lon = request.form.get("user_lon", "")

    # Save user data in the database
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO user_data (weight, lat, lon) VALUES (?, ?, ?)', (input_weight, input_lat, input_lon))
    db.commit()

    return f"Data saved: Weight={input_weight}, Lat={input_lat}, Lon={input_lon}"

if __name__ == "__main__":
    init_db()  # Initialize the database on app startup
    app.run(debug=True)
