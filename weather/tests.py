# tests.py

from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import FavoriteLocation, Profile
from .serializers import WeatherSerializer, ForecastSerializer, HistoricalWeatherSerializer
from .services import get_coordinates, get_current_weather, get_weather_forecast
from unittest.mock import patch
from django.urls import reverse

class ModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
    
    def test_create_favorite_location(self):
        location = FavoriteLocation.objects.create(user=self.user, city='New York')
        self.assertEqual(location.city, 'New York')
        self.assertEqual(location.user, self.user)
    
    def test_create_profile(self):
        profile = Profile.objects.get(user=self.user)
        self.assertFalse(profile.is_subscribed)
    
    def test_favorite_location_str(self):
        location = FavoriteLocation.objects.create(user=self.user, city='New York')
        self.assertEqual(str(location), 'New York')
    
    def test_profile_str(self):
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(str(profile), 'testuser')


class SerializersTestCase(TestCase):
    def test_weather_serializer(self):
        data = {
            'temperature': 23.5,
            'humidity': 80,
            'description': 'Cloudy',
            'wind_speed': 5.2,
            'icon': 'cloud'
        }
        serializer = WeatherSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_forecast_serializer(self):
        data = {
            'datetime': '2023-05-21 12:00:00',
            'temperature': 23.5,
            'humidity': 80,
            'description': 'Cloudy',
            'wind_speed': 5.2,
            'icon': 'cloud'
        }
        serializer = ForecastSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_historical_weather_serializer(self):
        data = {
            'datetime': '2023-05-21 12:00:00',
            'temperature': 23.5,
            'humidity': 80,
            'description': 'Cloudy',
            'wind_speed': 5.2,
            'icon': 'cloud'
        }
        serializer = HistoricalWeatherSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class ServicesTestCase(TestCase):
    @patch('weather.services.requests.get')
    def test_get_coordinates(self, mock_get):
        mock_get.return_value.json.return_value = {
            'coord': {'lat': 40.712776, 'lon': -74.005974}
        }
        mock_get.return_value.status_code = 200
        data = get_coordinates('New York')
        self.assertEqual(data['lat'], 40.712776)
    
    @patch('weather.services.requests.get')
    def test_get_current_weather(self, mock_get):
        mock_get.return_value.json.return_value = {
            'main': {'temp': 23.5, 'humidity': 80},
            'weather': [{'description': 'Cloudy', 'icon': 'cloud'}],
            'wind': {'speed': 5.2}
        }
        mock_get.return_value.status_code = 200
        data = get_current_weather('New York')
        self.assertEqual(data['temperature'], 23.5)
    
    @patch('weather.services.requests.get')
    def test_get_weather_forecast(self, mock_get):
        mock_get.return_value.json.return_value = {
            'list': [{
                'dt_txt': '2023-05-21 12:00:00',
                'main': {'temp': 23.5, 'humidity': 80},
                'weather': [{'description': 'Cloudy', 'icon': 'cloud'}],
                'wind': {'speed': 5.2}
            }]
        }
        mock_get.return_value.status_code = 200
        data = get_weather_forecast('New York')
        self.assertEqual(data[0]['temperature'], 23.5)


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
    
    @patch('weather.views.get_current_weather')
    def test_current_weather(self, mock_get_current_weather):
        mock_get_current_weather.return_value = {
            'temperature': 23.5,
            'humidity': 80,
            'description': 'Cloudy',
            'wind_speed': 5.2,
            'icon': 'cloud'
        }
        response = self.client.get(reverse('current_weather', args=['New York']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '23.5')
    
    @patch('weather.views.get_weather_forecast')
    def test_weather_forecast(self, mock_get_weather_forecast):
        mock_get_weather_forecast.return_value = [{
            'datetime': '2023-05-21 12:00:00',
            'temperature': 23.5,
            'humidity': 80,
            'description': 'Cloudy',
            'wind_speed': 5.2,
            'icon': 'cloud'
        }]
        response = self.client.get(reverse('weather_forecast', args=['New York']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '23.5')
    
    def test_add_favorite_location(self):
        response = self.client.post(reverse('add_favorite_location'), {'city': 'New York'})
        self.assertRedirects(response, reverse('favorite_locations'))
        self.assertTrue(FavoriteLocation.objects.filter(user=self.user, city='New York').exists())
    
    def test_favorite_locations(self):
        FavoriteLocation.objects.create(user=self.user, city='New York')
        response = self.client.get(reverse('favorite_locations'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New York')
    
    def test_subscribe(self):
        response = self.client.post(reverse('subscribe'))
        self.assertRedirects(response, reverse('personal_account'))
        self.assertTrue(Profile.objects.get(user=self.user).is_subscribed)
    
    def test_unsubscribe(self):
        profile = Profile.objects.get(user=self.user)
        profile.is_subscribed = True
        profile.save()
        response = self.client.post(reverse('unsubscribe'))
        self.assertRedirects(response, reverse('personal_account'))
        self.assertFalse(Profile.objects.get(user=self.user).is_subscribed)
