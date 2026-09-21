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

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius * c


def get_impact_radius(category):

    category = category.lower()

    if "wildfire" in category:
        return 50

    elif "severe storm" in category:
        return 500

    elif "volcano" in category:
        return 100

    elif "sea" in category:
        return 500

    else:
        return 100


def calculate_event_risk(distance, impact_radius):

    percentage = distance / impact_radius

    if percentage <= 0.25:
        return "EXTREME"

    elif percentage <= 0.50:
        return "HIGH"

    elif percentage <= 0.75:
        return "MODERATE"

    else:
        return "LOW"


def find_nearby_events(
    events_data,
    user_latitude,
    user_longitude
):

    nearby_events = []

    for event in events_data["events"]:

        geometry = event.get("geometry", [])

        if not geometry:
            continue

        coordinates = geometry[-1].get("coordinates")

        if not coordinates or len(coordinates) < 2:
            continue

        event_longitude = coordinates[0]
        event_latitude = coordinates[1]

        category = event["categories"][0]["title"]

        distance = calculate_distance(
            user_latitude,
            user_longitude,
            event_latitude,
            event_longitude
        )

        impact_radius = get_impact_radius(category)

        if distance <= impact_radius:

            risk = calculate_event_risk(
                distance,
                impact_radius
            )

            nearby_events.append({

                "event": event["title"],

                "category": category,

                "event_latitude": event_latitude,

                "event_longitude": event_longitude,

                "distance_km": round(
                    distance,
                    2
                ),

                "impact_radius_km":
                    impact_radius,

                "risk": risk,

                "person_at_risk": True

            })

    return nearby_events