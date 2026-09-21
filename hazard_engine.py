def calculate_overall_risk(weather_risks, flood_risk, natural_events):

    all_risks = []

    # Weather risks
    for item in weather_risks:
        all_risks.append(item["risk"])

    # Flood risk
    all_risks.append(flood_risk["risk"])

    # NASA natural-event risks
    for event in natural_events:
        all_risks.append(event["risk"])

    risk_score = {
        "LOW": 1,
        "MODERATE": 2,
        "HIGH": 3,
        "EXTREME": 4
    }

    highest_score = max(
        risk_score[risk]
        for risk in all_risks
    )

    for risk, score in risk_score.items():

        if score == highest_score:
            return risk