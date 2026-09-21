from math import radians, sin, cos, sqrt, atan2


def calculate_distance(lat1, lon1, lat2, lon2):

    earth_radius = 6371

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius * c


def get_affected_area(hazard_latitude, hazard_longitude, radius_km):

    # Approximate latitude/longitude boundaries
    latitude_change = radius_km / 111

    longitude_change = radius_km / (
        111 * cos(radians(hazard_latitude))
    )

    return {
        "center_latitude": hazard_latitude,
        "center_longitude": hazard_longitude,
        "radius_km": radius_km,
        "min_latitude": hazard_latitude - latitude_change,
        "max_latitude": hazard_latitude + latitude_change,
        "min_longitude": hazard_longitude - longitude_change,
        "max_longitude": hazard_longitude + longitude_change
    }


def is_location_affected(
    hazard_latitude,
    hazard_longitude,
    user_latitude,
    user_longitude,
    radius_km
):

    distance = calculate_distance(
        hazard_latitude,
        hazard_longitude,
        user_latitude,
        user_longitude
    )

    return distance <= radius_km