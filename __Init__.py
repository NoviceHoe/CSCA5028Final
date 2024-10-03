from app import app
from models import db

def init_db():
    with app.app_context():
        db.create_all()
        print("Database initialized and tables created.")

if __name__ == '__main__':
    init_db()
