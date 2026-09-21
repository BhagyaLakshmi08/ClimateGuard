from flask import Flask, render_template, request

from services.weather_service import get_weather
from services.flood_service import get_flood_data
from services.eonet_service import get_natural_events
from services.population_service import get_population_in_area

from hazards.weather_hazards import analyze_weather
from hazards.flood_hazards import analyze_flood
from hazards.eonet_hazards import find_nearby_events
from hazards.hazard_engine import calculate_overall_risk
from hazards.climate_risk import calculate_climate_risk


app = Flask(__name__)


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template(
        "location.html"
    )


# ==========================================
# ANALYZE USER LOCATION
# ==========================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    data = request.get_json()

    latitude = data["latitude"]
    longitude = data["longitude"]


    print("\n================================")
    print("CLIMATEGUARD USER LOCATION")
    print("================================")

    print(
        "Latitude:",
        latitude
    )

    print(
        "Longitude:",
        longitude
    )


    # ==========================================
    # WEATHER
    # ==========================================

    print("\nGetting weather data...")

    weather = get_weather(
        latitude,
        longitude
    )

    weather_risks = analyze_weather(
        weather
    )


    # ==========================================
    # FLOOD
    # ==========================================

    print("Getting flood data...")

    flood_data = get_flood_data(
        latitude,
        longitude
    )

    flood_risk = analyze_flood(
        flood_data
    )


    # ==========================================
    # NASA NATURAL EVENTS
    # ==========================================

    print("Getting NASA natural events...")

    events_data = get_natural_events()

    natural_events = find_nearby_events(
        events_data,
        latitude,
        longitude
    )


    # ==========================================
    # OVERALL HAZARD RISK
    # ==========================================

    overall_risk = calculate_overall_risk(
        weather_risks,
        flood_risk,
        natural_events
    )


    # ==========================================
    # AFFECTED AREA
    # ==========================================

    print("\nDetermining affected area...")


    if natural_events:

        affected_radius = natural_events[0][
            "impact_radius_km"
        ]

        affected_center_latitude = (
            natural_events[0][
                "event_latitude"
            ]
        )

        affected_center_longitude = (
            natural_events[0][
                "event_longitude"
            ]
        )

        affected_source = (
            "Nearby natural event"
        )


    else:

        if overall_risk == "EXTREME":

            affected_radius = 50

        elif overall_risk == "HIGH":

            affected_radius = 25

        elif overall_risk == "MODERATE":

            affected_radius = 10

        else:

            affected_radius = 5


        affected_center_latitude = latitude

        affected_center_longitude = longitude

        affected_source = (
            "Prototype risk-based estimate"
        )


    print(
        "Affected Radius:",
        affected_radius,
        "km"
    )

    print(
        "Affected Area Source:",
        affected_source
    )


    # ==========================================
    # POPULATION
    # ==========================================

    print(
        "Getting population data..."
    )


    population_data = get_population_in_area(

        affected_center_latitude,

        affected_center_longitude,

        affected_radius

    )


    # ==========================================
    # CLIMATE RISK SCORE
    # ==========================================

    print(
        "Calculating climate risk score..."
    )


    climate_risk = calculate_climate_risk(

        weather_risks,

        flood_risk,

        natural_events,

        population_data

    )


    # ==========================================
    # TERMINAL REPORT
    # ==========================================

    print("\n================================")
    print("CLIMATEGUARD MULTI-HAZARD REPORT")
    print("================================")


    print("\n--- Weather Hazards ---")

    for item in weather_risks:

        print(
            f"{item['hazard']}: "
            f"{item['risk']}"
        )


    print("\n--- Flood ---")

    print(
        f"Flood: {flood_risk['risk']}"
    )


    print("\n--- Natural Events ---")

    if natural_events:

        for event in natural_events:

            print(
                f"Event: {event['event']}"
            )

            print(
                f"Category: {event['category']}"
            )

            print(
                f"Distance: "
                f"{event['distance_km']} km"
            )

            print(
                f"Risk: {event['risk']}"
            )

    else:

        print(
            "No nearby natural events detected."
        )


    print("\n--- Affected Area ---")

    print(
        "Affected Radius:",
        affected_radius,
        "km"
    )

    print(
        "Affected Area Source:",
        affected_source
    )


    print("\n--- Population At Risk ---")

    print(
        "Estimated People in Area:",
        population_data["population"]
    )

    print(
        "Population Data Year:",
        population_data["data_year"]
    )


    print("\n--- Climate Risk Score ---")

    print(
        "Risk Score:",
        climate_risk["score"],
        "/ 100"
    )

    print(
        "Risk Level:",
        climate_risk["risk_level"]
    )

    print(
        "Weather Contribution:",
        climate_risk["weather_score"]
    )

    print(
        "Flood Contribution:",
        climate_risk["flood_score"]
    )

    print(
        "Natural Event Contribution:",
        climate_risk["natural_event_score"]
    )

    print(
        "Population Contribution:",
        climate_risk["population_score"]
    )


    print("\n--------------------------------")

    print(
        "OVERALL HAZARD RISK:",
        overall_risk
    )

    print(
        "CLIMATE RISK:",
        climate_risk["risk_level"]
    )

    print("--------------------------------")


    # ==========================================
    # SEND RESULTS TO BROWSER
    # ==========================================

    return {

        "latitude":
            latitude,

        "longitude":
            longitude,

        "weather_risks":
            weather_risks,

        "flood_risk":
            flood_risk,

        "natural_events":
            natural_events,

        "overall_risk":
            overall_risk,

        "affected_area": {

            "center_latitude":
                affected_center_latitude,

            "center_longitude":
                affected_center_longitude,

            "radius_km":
                affected_radius,

            "source":
                affected_source

        },

        "population":
            population_data,

        "climate_risk":
            climate_risk

    }


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )