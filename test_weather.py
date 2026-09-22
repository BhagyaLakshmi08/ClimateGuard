from hazards.affected_area import (
    get_dominant_hazard,
    get_affected_area
)


# Test hazard data

weather_risks = [

    {
        "hazard": "Heat",
        "risk": "LOW"
    },

    {
        "hazard": "Strong Wind",
        "risk": "LOW"
    },

    {
        "hazard": "Heavy Rain",
        "risk": "LOW"
    },

    {
        "hazard": "Thunderstorm",
        "risk": "LOW"
    }

]


flood_risk = {

    "hazard": "Flood",

    "risk": "LOW"

}


# Find dominant hazard

dominant = get_dominant_hazard(

    weather_risks,

    flood_risk

)


# Create affected area

affected_area = get_affected_area(

    16.4578548,

    80.5344060,

    dominant["hazard"],

    dominant["risk"]

)


print("\n======================================")

print(
    "CLIMATEGUARD AFFECTED AREA"
)

print("======================================")


print(
    "Dominant Hazard:",
    dominant["hazard"]
)


print(
    "Risk Level:",
    dominant["risk"]
)


print(
    "Affected Radius:",
    affected_area["radius_km"],
    "km"
)


print(
    "Source:",
    affected_area["source"]
)


print("======================================")
