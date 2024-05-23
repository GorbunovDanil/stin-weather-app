from django.test import TestCase
from .services import get_current_weather, get_weather_forecast

class WeatherServiceTests(TestCase):
    def test_get_current_weather(self):
        city = 'London'
        data = get_current_weather(city)
        self.assertIsNotNone(data)
        self.assertIn('main', data)
        self.assertIn('weather', data)
        self.assertIn('name', data)
        self.assertEqual(data['name'], city)

    def test_get_weather_forecast(self):
        city = 'London'
        data = get_weather_forecast(city)
        self.assertIsNotNone(data)
        self.assertIn('list', data)
        self.assertTrue(len(data['list']) > 0)
        self.assertIn('main', data['list'][0])
        self.assertIn('weather', data['list'][0])
