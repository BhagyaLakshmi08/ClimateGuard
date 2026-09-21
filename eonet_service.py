import requests


def get_natural_events():

    url = "https://eonet.gsfc.nasa.gov/api/v3/events"

    params = {
        "status": "open",
        "limit": 100
    }

    response = requests.get(url, params=params, timeout=10)

    response.raise_for_status()

    return response.json()