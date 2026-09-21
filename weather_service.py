import requests


def get_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "precipitation",
            "wind_speed_10m",
            "wind_gusts_10m",
            "weather_code"
        ],
        "hourly": [
            "precipitation_probability",
            "precipitation"
        ],
        "forecast_days": 2
    }

    response = requests.get(url, params=params, timeout=10)

    response.raise_for_status()

    return response.json()