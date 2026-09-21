def analyze_flood(flood_data):

    daily_data = flood_data["daily"]

    river_discharge = daily_data["river_discharge"]

    # Find the highest predicted river discharge
    maximum_discharge = max(river_discharge)

    # Prototype risk classification
    if maximum_discharge >= 1000:
        flood_risk = "EXTREME"

    elif maximum_discharge >= 500:
        flood_risk = "HIGH"

    elif maximum_discharge >= 100:
        flood_risk = "MODERATE"

    else:
        flood_risk = "LOW"

    return {
        "hazard": "Flood",
        "risk": flood_risk,
        "maximum_discharge": maximum_discharge
    }