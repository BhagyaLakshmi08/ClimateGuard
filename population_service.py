import requests
import json
import math


WORLDPOP_URL = "https://api.worldpop.org/v1/services/stats"


def create_circle_polygon(
    latitude,
    longitude,
    radius_km,
    number_of_points=36
):

    coordinates = []

    earth_radius = 6371

    for i in range(number_of_points + 1):

        angle = (
            2 * math.pi * i
            / number_of_points
        )

        latitude_change = (
            radius_km / earth_radius
        ) * math.cos(angle)

        longitude_change = (
            radius_km /
            (
                earth_radius *
                math.cos(
                    math.radians(latitude)
                )
            )
        ) * math.sin(angle)

        new_latitude = (
            latitude +
            math.degrees(latitude_change)
        )

        new_longitude = (
            longitude +
            math.degrees(longitude_change)
        )

        coordinates.append([
            new_longitude,
            new_latitude
        ])

    return {
        "type": "FeatureCollection",

        "features": [

            {
                "type": "Feature",

                "properties": {},

                "geometry": {

                    "type": "Polygon",

                    "coordinates": [
                        coordinates
                    ]

                }

            }

        ]

    }


def get_population_in_area(
    latitude,
    longitude,
    radius_km
):

    polygon = create_circle_polygon(
        latitude,
        longitude,
        radius_km
    )

    params = {

        "dataset": "wpgppop",

        "year": 2020,

        "geojson": json.dumps(
            polygon,
            separators=(",", ":")
        ),

        "runasync": "false"

    }

    print("Getting WorldPop population data...")

    response = requests.get(
        WORLDPOP_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if data.get("error"):

        raise Exception(
            data.get(
                "error_message",
                "WorldPop API error"
            )
        )

    population = (
        data
        .get("data", {})
        .get("total_population")
    )

    if population is None:

        raise Exception(
            "Population value was not returned by WorldPop."
        )

    return {

        "population": round(
            population
        ),

        "radius_km": radius_km,

        "latitude": latitude,

        "longitude": longitude,

        "data_year": 2020

    }