# ==========================================
# CLIMATEGUARD POPULATION EXPOSURE
# ==========================================


def get_exposure_percentage(
    hazard,
    risk
):

    hazard = hazard.lower()


    # ==========================================
    # FLOOD
    # ==========================================

    if "flood" in hazard:

        if risk == "EXTREME":
            return 0.90

        elif risk == "HIGH":
            return 0.75

        elif risk == "MODERATE":
            return 0.50

        else:
            return 0.20


    # ==========================================
    # HEAT
    # ==========================================

    elif "heat" in hazard:

        if risk == "EXTREME":
            return 0.80

        elif risk == "HIGH":
            return 0.60

        elif risk == "MODERATE":
            return 0.40

        else:
            return 0.15


    # ==========================================
    # HEAVY RAIN
    # ==========================================

    elif "rain" in hazard:

        if risk == "EXTREME":
            return 0.70

        elif risk == "HIGH":
            return 0.50

        elif risk == "MODERATE":
            return 0.30

        else:
            return 0.10


    # ==========================================
    # STRONG WIND
    # ==========================================

    elif "wind" in hazard:

        if risk == "EXTREME":
            return 0.80

        elif risk == "HIGH":
            return 0.60

        elif risk == "MODERATE":
            return 0.40

        else:
            return 0.15


    # ==========================================
    # THUNDERSTORM
    # ==========================================

    elif "thunderstorm" in hazard:

        if risk == "EXTREME":
            return 0.70

        elif risk == "HIGH":
            return 0.50

        elif risk == "MODERATE":
            return 0.30

        else:
            return 0.10


    # ==========================================
    # DEFAULT
    # ==========================================

    return 0.10


# ==========================================
# CALCULATE PEOPLE EXPOSED
# ==========================================

def calculate_people_at_risk(
    population,
    hazard,
    risk
):

    exposure_percentage = (
        get_exposure_percentage(
            hazard,
            risk
        )
    )


    people_at_risk = round(
        population *
        exposure_percentage
    )


    return {

        "total_population":
            population,

        "exposure_percentage":
            round(
                exposure_percentage * 100,
                1
            ),

        "people_at_risk":
            people_at_risk,

        "hazard":
            hazard,

        "risk":
            risk

    }