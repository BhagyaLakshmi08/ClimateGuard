def analyze_weather(weather):

    current = weather["current"]

    temperature = current["temperature_2m"]
    precipitation = current["precipitation"]
    wind_gusts = current["wind_gusts_10m"]
    weather_code = current["weather_code"]

    risks = []

    # Heat Risk
    if temperature >= 40:
        heat_risk = "EXTREME"
    elif temperature >= 37:
        heat_risk = "HIGH"
    elif temperature >= 35:
        heat_risk = "MODERATE"
    else:
        heat_risk = "LOW"

    risks.append({
        "hazard": "Heat",
        "risk": heat_risk
    })

    # Strong Wind Risk
    if wind_gusts >= 70:
        wind_risk = "EXTREME"
    elif wind_gusts >= 50:
        wind_risk = "HIGH"
    elif wind_gusts >= 35:
        wind_risk = "MODERATE"
    else:
        wind_risk = "LOW"

    risks.append({
        "hazard": "Strong Wind",
        "risk": wind_risk
    })

    # Heavy Rain Risk
    if precipitation >= 50:
        rain_risk = "EXTREME"
    elif precipitation >= 20:
        rain_risk = "HIGH"
    elif precipitation >= 5:
        rain_risk = "MODERATE"
    else:
        rain_risk = "LOW"

    risks.append({
        "hazard": "Heavy Rain",
        "risk": rain_risk
    })

    # Thunderstorm Risk
    if weather_code in [95, 96, 99]:
        thunderstorm_risk = "HIGH"
    else:
        thunderstorm_risk = "LOW"

    risks.append({
        "hazard": "Thunderstorm",
        "risk": thunderstorm_risk
    })

    return risks