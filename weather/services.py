import requests
from datetime import datetime

API_KEY = '671f60305315c4183fb5dea98473574f'
BASE_URL = 'http://api.openweathermap.org/data/2.5/'

def get_coordinates(city):
    url = f"{BASE_URL}weather?q={city}&appid={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(f"Coordinates for {city}: {data['coord']['lat']}, {data['coord']['lon']}")  # Debug
        return data['coord']['lat'], data['coord']['lon']
    else:
        print(f"Failed to get coordinates for {city}. Status code: {response.status_code}")  # Debug
        return None, None

def get_current_weather(city):
    url = f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_weather_forecast(city):
    url = f"{BASE_URL}forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
