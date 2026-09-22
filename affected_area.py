from math import radians, sin, cos, sqrt, atan2


def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    earth_radius = 6371

    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return earth_radius * c


# ==========================================
# HAZARD-SPECIFIC RADIUS
# ==========================================

def get_hazard_radius(
    hazard,
    risk
):

    hazard = hazard.lower()

    # --------------------------------------
    # FLOOD
    # --------------------------------------

    if "flood" in hazard:

        if risk == "EXTREME":
            return 20

        elif risk == "HIGH":
            return 15

        elif risk == "MODERATE":
            return 10

        else:
            return 5


    # --------------------------------------
    # HEAT
    # --------------------------------------

    elif "heat" in hazard:

        if risk == "EXTREME":
            return 30

        elif risk == "HIGH":
            return 20

        elif risk == "MODERATE":
            return 15

        else:
            return 5


    # --------------------------------------
    # HEAVY RAIN
    # --------------------------------------

    elif "rain" in hazard:

        if risk == "EXTREME":
            return 15

        elif risk == "HIGH":
            return 10

        elif risk == "MODERATE":
            return 7

        else:
            return 5


    # --------------------------------------
    # STRONG WIND
    # --------------------------------------

    elif "wind" in hazard:

        if risk == "EXTREME":
            return 30

        elif risk == "HIGH":
            return 20

        elif risk == "MODERATE":
            return 10

        else:
            return 5


    # --------------------------------------
    # THUNDERSTORM
    # --------------------------------------

    elif "thunderstorm" in hazard:

        if risk == "HIGH":
            return 15

        elif risk == "MODERATE":
            return 10

        else:
            return 5


    # --------------------------------------
    # DEFAULT
    # --------------------------------------

    return 5


# ==========================================
# FIND DOMINANT WEATHER HAZARD
# ==========================================

def get_dominant_hazard(
    weather_risks,
    flood_risk
):

    priority = {
        "LOW": 1,
        "MODERATE": 2,
        "HIGH": 3,
        "EXTREME": 4
    }


    dominant_hazard = "General"

    dominant_risk = "LOW"

    dominant_score = 0


    # Weather hazards

    for item in weather_risks:

        score = priority.get(
            item["risk"],
            0
        )

        if score > dominant_score:

            dominant_score = score

            dominant_hazard = item["hazard"]

            dominant_risk = item["risk"]


    # Flood

    flood_score = priority.get(
        flood_risk["risk"],
        0
    )


    if flood_score > dominant_score:

        dominant_hazard = "Flood"

        dominant_risk = flood_risk["risk"]


    return {
        "hazard": dominant_hazard,
        "risk": dominant_risk
    }


# ==========================================
# AFFECTED AREA
# ==========================================

def get_affected_area(
    latitude,
    longitude,
    hazard,
    risk
):

    radius_km = get_hazard_radius(
        hazard,
        risk
    )


    return {

        "center_latitude":
            latitude,

        "center_longitude":
            longitude,

        "radius_km":
            radius_km,

        "hazard":
            hazard,

        "risk":
            risk,

        "source":
            "Prototype hazard-specific model"

    }


# ==========================================
# CHECK IF PERSON IS AFFECTED
# ==========================================

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
