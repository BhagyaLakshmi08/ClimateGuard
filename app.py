from flask import Flask, render_template, request, jsonify

from services.weather_service import get_weather
from services.flood_service import get_flood_data
from services.eonet_service import get_natural_events
from services.population_service import get_population_in_area

from hazards.weather_hazards import analyze_weather
from hazards.flood_hazards import analyze_flood
from hazards.eonet_hazards import find_nearby_events
from hazards.hazard_engine import calculate_overall_risk
from hazards.climate_risk import calculate_climate_risk

from hazards.affected_area import (
    get_dominant_hazard,
    get_affected_area
)

from hazards.exposure import (
    calculate_people_at_risk
)


app = Flask(__name__)


# ============================================================
# LATEST ANALYSIS
# Used by Government Dashboard
# ============================================================

latest_analysis = None


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "location.html"
    )


# ============================================================
# GLOBAL / LOCAL HAZARD MAP
#
# mode=user        -> Citizen map
# mode=government  -> Government map
# ============================================================

@app.route("/map")
def hazard_map():

    mode = request.args.get(
        "mode",
        "user"
    )

    return render_template(
        "map.html",
        mode=mode
    )


# ============================================================
# CLIMATEGUARD ANALYSIS
# ============================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    global latest_analysis

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


    # ========================================================
    # WEATHER
    # ========================================================

    print("\nGetting weather data...")

    weather = get_weather(
        latitude,
        longitude
    )

    weather_risks = analyze_weather(
        weather
    )


    # ========================================================
    # FLOOD
    # ========================================================

    print("Getting flood data...")

    flood_data = get_flood_data(
        latitude,
        longitude
    )

    flood_risk = analyze_flood(
        flood_data
    )


    # ========================================================
    # NASA NATURAL EVENTS
    # ========================================================

    print(
        "Getting NASA natural events..."
    )

    events_data = get_natural_events()

    natural_events = find_nearby_events(
        events_data,
        latitude,
        longitude
    )


    # ========================================================
    # OVERALL HAZARD RISK
    # ========================================================

    overall_risk = calculate_overall_risk(
        weather_risks,
        flood_risk,
        natural_events
    )


    # ========================================================
    # DOMINANT HAZARD
    # ========================================================

    print(
        "\nDetermining dominant hazard..."
    )

    dominant = get_dominant_hazard(
        weather_risks,
        flood_risk
    )


    print(
        "Dominant Hazard:",
        dominant["hazard"]
    )

    print(
        "Dominant Risk:",
        dominant["risk"]
    )


    # ========================================================
    # AFFECTED AREA
    # ========================================================

    affected_area = get_affected_area(
        latitude,
        longitude,
        dominant["hazard"],
        dominant["risk"]
    )


    print(
        "Affected Radius:",
        affected_area["radius_km"],
        "km"
    )

    print(
        "Affected Area Source:",
        affected_area["source"]
    )


    # ========================================================
    # POPULATION
    # ========================================================

    print(
        "\nGetting population data..."
    )

    population_data = get_population_in_area(

        affected_area[
            "center_latitude"
        ],

        affected_area[
            "center_longitude"
        ],

        affected_area[
            "radius_km"
        ]

    )


    print(
        "Estimated Population:",
        population_data["population"]
    )


    # ========================================================
    # PEOPLE AT RISK
    # ========================================================

    print(
        "Calculating population exposure..."
    )

    people_at_risk = calculate_people_at_risk(

        population_data[
            "population"
        ],

        affected_area[
            "hazard"
        ],

        affected_area[
            "risk"
        ]

    )


    print(
        "Exposure Percentage:",
        people_at_risk[
            "exposure_percentage"
        ],
        "%"
    )


    print(
        "Estimated People At Risk:",
        people_at_risk[
            "people_at_risk"
        ]
    )


    # ========================================================
    # CLIMATE RISK SCORE
    # ========================================================

    print(
        "Calculating climate risk score..."
    )

    climate_risk = calculate_climate_risk(

        weather_risks,

        flood_risk,

        natural_events,

        population_data

    )


    # ========================================================
    # TERMINAL REPORT
    # ========================================================

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
        f"Flood: "
        f"{flood_risk['risk']}"
    )


    print("\n--- Natural Events ---")


    if natural_events:

        for event in natural_events:

            print(
                f"Event: "
                f"{event['event']}"
            )

            print(
                f"Category: "
                f"{event['category']}"
            )

            print(
                f"Distance: "
                f"{event['distance_km']} km"
            )

            print(
                f"Risk: "
                f"{event['risk']}"
            )

    else:

        print(
            "No nearby natural events detected."
        )


    print("\n--- Affected Area ---")

    print(
        "Dominant Hazard:",
        affected_area["hazard"]
    )

    print(
        "Risk:",
        affected_area["risk"]
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


    print("\n--- Population Exposure ---")

    print(
        "Estimated Population:",
        population_data["population"]
    )

    print(
        "Exposure Percentage:",
        people_at_risk[
            "exposure_percentage"
        ],
        "%"
    )

    print(
        "Estimated People At Risk:",
        people_at_risk[
            "people_at_risk"
        ]
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


    # ========================================================
    # SAVE LATEST ANALYSIS
    # Government Dashboard will use this
    # ========================================================

    latest_analysis = {

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

        "affected_area":
            affected_area,

        "population":
            population_data,

        "people_at_risk":
            people_at_risk,

        "climate_risk":
            climate_risk

    }


    # ========================================================
    # RETURN DATA TO CITIZEN FRONTEND
    # ========================================================

    return jsonify({

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
                affected_area[
                    "center_latitude"
                ],

            "center_longitude":
                affected_area[
                    "center_longitude"
                ],

            "radius_km":
                affected_area[
                    "radius_km"
                ],

            "hazard":
                affected_area[
                    "hazard"
                ],

            "risk":
                affected_area[
                    "risk"
                ],

            "source":
                affected_area[
                    "source"
                ]

        },

        "population":
            population_data,

        "people_at_risk":
            people_at_risk,

        "climate_risk":
            climate_risk

    })


# ============================================================
# GOVERNMENT COMMAND CENTER
# ============================================================

@app.route("/government")
def government():

    return render_template(
        "government.html"
    )


# ============================================================
# GOVERNMENT DASHBOARD DATA
# ============================================================

@app.route("/government-data")
def government_data():

    if latest_analysis is None:

        return jsonify({

            "available":
                False

        })


    return jsonify({

        "available":
            True,

        "data":
            latest_analysis

    })


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
