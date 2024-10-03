import unittest
from flask import Flask
from flask.testing import FlaskClient
from models import db, User
from app import app, fetch_max_daily_temperature
from unittest.mock import patch

class FlaskAppTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup the test environment
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_users.db'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        db.init_app(app)
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        # Remove the test database after the test suite
        with app.app_context():
            db.drop_all()

    def setUp(self):
        # Setup the test client
        self.client = app.test_client()

    def tearDown(self):
        # Clean up the database after each test
        with app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()

    def test_index_get(self):
        # Test the GET request for the index page
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Enter Weight', response.data)  # Replace with actual form element text

    def test_index_post_valid_data(self):
        # Mock the API call to return a fixed temperature value
        with patch('app.fetch_max_daily_temperature') as mock_fetch:
            mock_fetch.return_value = 75.0

            # Post valid data to the form
            response = self.client.post('/', data={
                'weight': 70,
                'latitude': 40.7128,
                'longitude': -74.0060
            })

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Result', response.data)  # Check for result in response

            # Check that user was added to the database
            with app.app_context():
                user = User.query.first()
                self.assertIsNotNone(user)
                self.assertEqual(user.weight, 70)
                self.assertEqual(user.latitude, 40.7128)
                self.assertEqual(user.longitude, -74.0060)

    def test_index_post_invalid_data(self):
        # Test posting invalid data to the form (e.g., non-float values)
        response = self.client.post('/', data={
            'weight': 'invalid',
            'latitude': 'invalid',
            'longitude': 'invalid'
        })

        self.assertEqual(response.status_code, 400)  # Expecting a 400 due to invalid input

    @patch('app.fetch_max_daily_temperature')
    def test_fetch_max_daily_temperature(self, mock_fetch):
        # Test the fetch_max_daily_temperature function with a mock response
        mock_fetch.return_value = 75.0

        # Test with valid lat/long values
        temp = fetch_max_daily_temperature(40.7128, -74.0060)
        self.assertEqual(temp, 75.0)

    def test_create_user(self):
        # Test creating a user and saving to the database
        with app.app_context():
            user = User(weight=150.5, latitude=34.05, longitude=-118.25)
            db.session.add(user)
            db.session.commit()

            saved_user = User.query.filter_by(latitude=34.05).first()
            self.assertIsNotNone(saved_user)
            self.assertEqual(saved_user.weight, 150.5)

if __name__ == '__main__':
    unittest.main()
