import unittest
from unittest.mock import patch
from app import app, db, User

class FlaskAppIntegrationTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up the test environment
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///integration_test_users.db'
        app.config['TESTING'] = True
        db.init_app(app)
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        # Clean up the test environment after all tests
        with app.app_context():
            db.drop_all()

    def setUp(self):
        # Set up the test client
        self.client = app.test_client()

    def tearDown(self):
        # Clean up the database after each test
        with app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()

    @patch('app.fetch_max_daily_temperature')
    def test_full_form_submission_flow(self, mock_fetch):
        # Mock the API call to simulate fetching a maximum daily temperature
        mock_fetch.return_value = 75.0  # Fahrenheit

        # Simulate form submission with valid data
        response = self.client.post('/', data={
            'weight': '70',
            'latitude': '40.7128',
            'longitude': '-74.0060'
        })

        # Check the response is successful
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Result', response.data)  # Ensure the result is displayed in the response

        # Verify that a user has been added to the database
        with app.app_context():
            user = User.query.first()
            self.assertIsNotNone(user)
            self.assertEqual(user.weight, 70.0)
            self.assertEqual(user.latitude, 40.7128)
            self.assertEqual(user.longitude, -74.0060)
            self.assertEqual(user.max_daily_temp, 75.0)

    def test_index_page_loads_correctly(self):
        # Test if the index page loads correctly
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Enter Weight', response.data)  # Replace with actual form element text for validation

    @patch('app.fetch_max_daily_temperature')
    def test_form_submission_invalid_temperature(self, mock_fetch):
        # Mock the API call to simulate an error in fetching temperature
        mock_fetch.return_value = None

        # Simulate form submission
        response = self.client.post('/', data={
            'weight': '70',
            'latitude': '40.7128',
            'longitude': '-74.0060'
        })

        # Check if the proper error message is returned when temperature data cannot be retrieved
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Weather data could not be retrieved. Please try again later.', response.data)

if __name__ == '__main__':
    unittest.main()
