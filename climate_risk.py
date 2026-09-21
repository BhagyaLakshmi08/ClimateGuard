def calculate_climate_risk(
    weather_risks,
    flood_risk,
    natural_events,
    population
):

    # ==========================================
    # WEATHER SCORE
    # ==========================================

    risk_values = {
        "LOW": 0,
        "MODERATE": 10,
        "HIGH": 20,
        "EXTREME": 30
    }

    weather_score = 0

    for item in weather_risks:

        weather_score += risk_values.get(
            item["risk"],
            0
        )


    # Maximum weather contribution = 30
    weather_score = min(
        weather_score,
        30
    )


    # ==========================================
    # FLOOD SCORE
    # ==========================================

    flood_score = risk_values.get(
        flood_risk["risk"],
        0
    )

    # Maximum flood contribution = 30
    flood_score = min(
        flood_score,
        30
    )


    # ==========================================
    # NATURAL EVENT SCORE
    # ==========================================

    natural_event_score = 0

    for event in natural_events:

        event_score = risk_values.get(
            event["risk"],
            0
        )

        natural_event_score = max(
            natural_event_score,
            event_score
        )


    # Maximum natural-event contribution = 30
    natural_event_score = min(
        natural_event_score,
        30
    )


    # ==========================================
    # POPULATION EXPOSURE SCORE
    # ==========================================

    population_value = population["population"]


    if population_value >= 100000:

        population_score = 10

    elif population_value >= 50000:

        population_score = 8

    elif population_value >= 25000:

        population_score = 6

    elif population_value >= 10000:

        population_score = 4

    elif population_value >= 5000:

        population_score = 2

    else:

        population_score = 1


    # ==========================================
    # TOTAL SCORE
    # ==========================================

    total_score = (
        weather_score
        + flood_score
        + natural_event_score
        + population_score
    )


    # Keep score between 0 and 100

    total_score = min(
        total_score,
        100
    )


    # ==========================================
    # RISK LEVEL
    # ==========================================

    if total_score >= 75:

        risk_level = "EXTREME"

    elif total_score >= 50:

        risk_level = "HIGH"

    elif total_score >= 25:

        risk_level = "MODERATE"

    else:

        risk_level = "LOW"


    return {

        "score": total_score,

        "risk_level": risk_level,

        "weather_score": weather_score,

        "flood_score": flood_score,

        "natural_event_score":
            natural_event_score,

        "population_score":
            population_score,

        "population":
            population_value

    }