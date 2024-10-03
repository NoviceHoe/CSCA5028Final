from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    max_daily_temp = db.Column(db.Float, nullable=True)  # New field for max daily temperature

    def __repr__(self):
        return f'<User {self.id}: Weight={self.weight}, Lat={self.latitude}, Long={self.longitude}, Max Temp={self.max_daily_temp}>'
