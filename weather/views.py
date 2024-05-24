from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponseNotAllowed
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .forms import RegisterForm
from .models import FavoriteLocation, Profile
from .services import get_current_weather, get_weather_forecast
from .serializers import WeatherSerializer, ForecastSerializer

@login_required
def home(request):
    return render(request, 'weather/home.html')

@login_required
def personal_account(request):
    profile = request.user.profile
    context = {
        'username': request.user.username,
        'is_subscribed': profile.is_subscribed
    }
    return render(request, 'weather/personal_account.html', context)


# User registration view
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'weather/register.html', {'form': form})

# User login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('current_weather')
    else:
        form = AuthenticationForm()
    return render(request, 'weather/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('current_weather')

# API view to get current weather
@api_view(['GET'])
def current_weather_api(request):
    city = request.GET.get('city', 'London')  # Default to London if no city is provided
    weather_data = get_current_weather(city)
    if weather_data:
        data = {
            'temperature': weather_data['main']['temp'],
            'humidity': weather_data['main']['humidity'],
            'description': weather_data['weather'][0]['description'],
            'wind_speed': weather_data['wind']['speed'],
            'icon': weather_data['weather'][0]['icon']
        }
        serializer = WeatherSerializer(data)
        return Response(serializer.data)
    else:
        return Response({'error': 'Could not fetch weather data'}, status=400)

# API view to get weather forecast
@api_view(['GET'])
def weather_forecast_api(request):
    city = request.GET.get('city', 'London')  # Default to London if no city is provided
    forecast_data = get_weather_forecast(city)
    if forecast_data:
        forecast_list = []
        for item in forecast_data['list']:
            forecast_list.append({
                'datetime': item['dt_txt'],
                'temperature': item['main']['temp'],
                'humidity': item['main']['humidity'],
                'description': item['weather'][0]['description'],
                'wind_speed': item['wind']['speed'],
                'icon': item['weather'][0]['icon']
            })
        serializer = ForecastSerializer(forecast_list, many=True)
        return Response(serializer.data)
    else:
        return Response({'error': 'Could not fetch weather forecast data'}, status=400)

# Helper function to call API view directly
def call_api_view(view_func, request, params):
    django_request = HttpRequest()
    django_request.method = request.method
    django_request.GET = params
    return view_func(django_request)

# View to render current weather using the API
def current_weather(request):
    city = request.GET.get('city', 'London')  # Default to London if no city is provided
    response = call_api_view(current_weather_api, request, {'city': city})
    if response.status_code == 200:
        weather_data = response.data
        context = {
            'city': city,
            'weather_data': weather_data
        }
    else:
        context = {
            'city': city,
            'error': 'Could not fetch weather data'
        }
    return render(request, 'weather/current_weather.html', context)

# View to render weather forecast using the API
@login_required
def weather_forecast(request, city):
    if not request.user.profile.is_subscribed:
        return redirect('subscribe')
    
    response = call_api_view(weather_forecast_api, request, {'city': city})
    if response.status_code == 200:
        forecast_data = response.data
        context = {
            'city': city,
            'forecast_data': forecast_data
        }
    else:
        context = {
            'city': city,
            'error': 'Could not fetch weather forecast data'
        }
    return render(request, 'weather/weather_forecast.html', context)

# View to add favorite location
@login_required
def add_favorite_location(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        if city:
            FavoriteLocation.objects.get_or_create(user=request.user, city=city)
    return redirect('favorite_locations')

# View to display favorite locations
@login_required
def favorite_locations(request):
    locations = FavoriteLocation.objects.filter(user=request.user)
    context = {
        'locations': locations
    }
    return render(request, 'weather/favorite_locations.html', context)

# Subscription views
@login_required
def subscribe(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile.is_subscribed = True
        profile.save()
        return redirect('personal_account')
    return render(request, 'weather/subscribe.html')

@login_required
def unsubscribe(request):
    profile = request.user.profile
    if request.method == 'POST':
        profile.is_subscribed = False
        profile.save()
        return redirect('personal_account')
    return render(request, 'weather/unsubscribe.html')