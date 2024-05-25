# weather/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch
from weather.services import get_coordinates, get_current_weather, get_weather_forecast
from weather.models import FavoriteLocation, Profile

class WeatherViewsTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        Profile.objects.get_or_create(user=self.user, defaults={'is_subscribed': True})
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.home_url = reverse('home')
        self.register_url = reverse('register')
        self.account_url = reverse('personal_account')
        self.add_favorite_url = reverse('add_favorite_location')
        self.favorites_url = reverse('favorite_locations')
        self.current_weather_url = reverse('current_weather')
        self.weather_forecast_url = reverse('weather_forecast', args=['London'])
        self.subscribe_url = reverse('subscribe')
        self.unsubscribe_url = reverse('unsubscribe')

    # def test_home_view(self):
    #     self.client.login(username='testuser', password='testpassword')
    #     response = self.client.get(self.home_url + '/')  # Ensure the URL ends with a slash
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'weather/home.html')

    def test_register_view(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/register.html')

    # def test_register_view_post(self):
    #     response = self.client.post(self.register_url, {
    #         'username': 'newuser',
    #         'password1': 'newpassword123',
    #         'password2': 'newpassword123'
    #     })
    #     self.assertEqual(response.status_code, 302)
    #     self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_personal_account_view_unauthenticated(self):
        response = self.client.get(self.account_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{self.login_url}?next={self.account_url}')

    def test_personal_account_view_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.account_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/personal_account.html')

    def test_add_favorite_location_view_unauthenticated(self):
        response = self.client.post(self.add_favorite_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{self.login_url}?next={self.add_favorite_url}')

    def test_add_favorite_location_view_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.add_favorite_url, {'city': 'London'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.favorites_url)
        favorites = FavoriteLocation.objects.filter(user=self.user)
        self.assertEqual(favorites.count(), 1)

    def test_favorite_locations_view_unauthenticated(self):
        response = self.client.get(self.favorites_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{self.login_url}?next={self.favorites_url}')

    def test_favorite_locations_view_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.favorites_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/favorite_locations.html')

    def test_login_view(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_post(self):
        response = self.client.post(self.login_url, {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.current_weather_url)

    def test_logout_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.current_weather_url)

    def test_current_weather_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.current_weather_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/current_weather.html')

    def test_weather_forecast_view_unauthenticated(self):
        response = self.client.get(self.weather_forecast_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{self.login_url}?next={self.weather_forecast_url}')

    def test_weather_forecast_view_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        profile = self.user.profile
        profile.is_subscribed = True
        profile.save()
        response = self.client.get(self.weather_forecast_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/weather_forecast.html')

    def test_subscribe_view_get(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.subscribe_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/subscribe.html')

    def test_subscribe_view_post(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.subscribe_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.account_url)
        self.user.refresh_from_db()
        self.assertTrue(self.user.profile.is_subscribed)

    def test_unsubscribe_view_get(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.unsubscribe_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/unsubscribe.html')

    def test_unsubscribe_view_post(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.unsubscribe_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.account_url)
        self.user.refresh_from_db()
        self.assertFalse(self.user.profile.is_subscribed)


class WeatherServicesTests(TestCase):

    @patch('weather.services.requests.get')
    def test_get_coordinates_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'coord': {'lat': 51.5074, 'lon': -0.1278}  # Example coordinates for London
        }
        lat, lon = get_coordinates('London')
        self.assertEqual(lat, 51.5074)
        self.assertEqual(lon, -0.1278)

    @patch('weather.services.requests.get')
    def test_get_coordinates_failure(self, mock_get):
        mock_get.return_value.status_code = 404
        lat, lon = get_coordinates('InvalidCity')
        self.assertIsNone(lat)
        self.assertIsNone(lon)

    @patch('weather.services.requests.get')
    def test_get_current_weather_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'main': {'temp': 15},
            'weather': [{'description': 'clear sky'}]
        }
        data = get_current_weather('London')
        self.assertIsNotNone(data)
        self.assertIn('main', data)
        self.assertIn('weather', data)

    @patch('weather.services.requests.get')
    def test_get_current_weather_failure(self, mock_get):
        mock_get.return_value.status_code = 404
        data = get_current_weather('InvalidCity')
        self.assertIsNone(data)

    @patch('weather.services.requests.get')
    def test_get_weather_forecast_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            'list': [{'dt_txt': '2024-05-23 12:00:00', 'main': {'temp': 15}, 'weather': [{'description': 'clear sky'}]}]
        }
        data = get_weather_forecast('London')
        self.assertIsNotNone(data)
        self.assertIn('list', data)

    @patch('weather.services.requests.get')
    def test_get_weather_forecast_failure(self, mock_get):
        mock_get.return_value.status_code = 404
        data = get_weather_forecast('InvalidCity')
        self.assertIsNone(data)
