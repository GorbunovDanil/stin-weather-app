from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register, home, current_weather, weather_forecast, add_favorite_location, favorite_locations, personal_account, subscribe, unsubscribe, logout_view

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='weather/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('current-weather/', current_weather, name='current_weather'),
    path('weather-forecast/<str:city>/', weather_forecast, name='weather_forecast'),
    path('weather-forecast/', weather_forecast, name='weather_forecast_default'),
    path('add-favorite/', add_favorite_location, name='add_favorite_location'),
    path('favorites/', favorite_locations, name='favorite_locations'),
    path('account/', personal_account, name='personal_account'),
    path('subscribe/', subscribe, name='subscribe'),
    path('unsubscribe/', unsubscribe, name='unsubscribe'),
]
