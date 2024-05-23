from django.urls import path
from .views import current_weather_api, weather_forecast_api

urlpatterns = [
    path('current-weather/', current_weather_api, name='current_weather_api'),
    path('weather-forecast/', weather_forecast_api, name='weather_forecast_api'),
]
