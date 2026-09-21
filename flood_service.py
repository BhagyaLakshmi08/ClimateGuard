import requests


def get_flood_data(latitude, longitude):

    url = "https://flood-api.open-meteo.com/v1/flood"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": [
            "river_discharge"
        ],
        "forecast_days": 7
    }

    response = requests.get(url, params=params, timeout=10)

    response.raise_for_status()

    return response.json()