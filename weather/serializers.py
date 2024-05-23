from rest_framework import serializers

class WeatherSerializer(serializers.Serializer):
    temperature = serializers.FloatField()
    humidity = serializers.IntegerField()
    description = serializers.CharField()
    wind_speed = serializers.FloatField()
    icon = serializers.CharField()

class ForecastSerializer(serializers.Serializer):
    datetime = serializers.CharField()
    temperature = serializers.FloatField()
    humidity = serializers.IntegerField()
    description = serializers.CharField()
    wind_speed = serializers.FloatField()
    icon = serializers.CharField()

class HistoricalWeatherSerializer(serializers.Serializer):
    datetime = serializers.CharField()
    temperature = serializers.FloatField()
    humidity = serializers.IntegerField()
    description = serializers.CharField()
    wind_speed = serializers.FloatField()
    icon = serializers.CharField()
