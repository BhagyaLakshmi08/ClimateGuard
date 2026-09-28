from flask import Flask, render_template, request, jsonify
from datetime import datetime

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


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# LATEST ANALYSIS
# Used by the Government Dashboard
# ============================================================

latest_analysis = None


# ============================================================
# GOVERNMENT ALERTS
#
# Temporary in-memory storage.
# Database will be added in a later stage.
# ============================================================

government_alerts = []


# ============================================================
# GOVERNMENT MONITORING REGIONS
# Approximate city-center coordinates
# ============================================================

GOVERNMENT_REGIONS = {

    "chennai": {

        "name": "Chennai",

        "latitude": 13.0827,

        "longitude": 80.2707

    },

    "coimbatore": {

        "name": "Coimbatore",

        "latitude": 11.0168,

        "longitude": 76.9558

    },

    "madurai": {

        "name": "Madurai",

        "latitude": 9.9252,

        "longitude": 78.1198

    },

    "tiruchirappalli": {

        "name": "Tiruchirappalli",

        "latitude": 10.7905,

        "longitude": 78.7047

    }

}


# ============================================================
# HELPER - GET RISK LEVEL
# ============================================================

def get_risk_level(value):

    if value is None:

        return "LOW"


    if isinstance(value, dict):

        level = (

            value.get("risk_level")

            or value.get("risk")

            or value.get("level")

            or "LOW"

        )

        return str(level).upper()


    return str(value).upper()


# ============================================================
# HELPER - WEATHER HAZARD RISK
# ============================================================

def get_weather_hazard_risk(
    weather_risks,
    keywords
):

    levels = []


    for item in weather_risks or []:

        if not isinstance(item, dict):

            continue


        hazard = str(
            item.get("hazard", "")
        ).lower()


        if any(
            keyword in hazard
            for keyword in keywords
        ):

            levels.append(
                get_risk_level(item)
            )


    if "HIGH" in levels:

        return "HIGH"


    if "MEDIUM" in levels:

        return "MEDIUM"


    return "LOW"


# ============================================================
# HELPER - INFRASTRUCTURE AT RISK
#
# This is a project estimate until an actual
# infrastructure dataset is connected.
# ============================================================

def estimate_infrastructure_at_risk(
    population,
    risk_level
):

    population = max(
        0,
        int(population or 0)
    )


    multiplier = {

        "HIGH": 1.0,

        "MEDIUM": 0.6,

        "LOW": 0.3

    }.get(

        risk_level,

        0.3

    )


    return round(

        (population / 1000)
        * multiplier

    )


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "location.html"
    )


# ============================================================
# MAP
#
# mode=user
# mode=government
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
# CLIMATEGUARD USER ANALYSIS
# ============================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    global latest_analysis


    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "error":
                "No JSON data received."

        }), 400


    if (
        "latitude" not in data
        or "longitude" not in data
    ):

        return jsonify({

            "error":
                "Latitude and longitude are required."

        }), 400


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

    print(
        "\nGetting weather data..."
    )


    weather = get_weather(

        latitude,

        longitude

    )


    weather_analysis = analyze_weather(



        weather



    )



    weather_risks = weather_analysis["risks"]



    weather_overall_score = weather_analysis["overall_score"]



    weather_overall_risk = weather_analysis["overall_risk"]


    # ========================================================
    # FLOOD
    # ========================================================

    print(
        "Getting flood data..."
    )


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
    # CLIMATE RISK
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


    print(
        "\n--- Weather Hazards ---"
    )


    for item in weather_risks:

        print(

            f"{item['hazard']}: "
            f"{item['risk']}"

        )


    print(
        "\n--- Flood ---"
    )


    print(

        f"Flood: "
        f"{flood_risk['risk']}"

    )


    print(
        "\n--- Natural Events ---"
    )


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


    print(
        "\n--- Affected Area ---"
    )


    print(

        "Dominant Hazard:",

        affected_area[
            "hazard"
        ]

    )


    print(

        "Risk:",

        affected_area[
            "risk"
        ]

    )


    print(

        "Affected Radius:",

        affected_area[
            "radius_km"
        ],

        "km"

    )


    print(

        "Source:",

        affected_area[
            "source"
        ]

    )


    print(
        "\n--- Population Exposure ---"
    )


    print(

        "Estimated Population:",

        population_data[
            "population"
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


    print(

        "Population Data Year:",

        population_data[
            "data_year"
        ]

    )


    print(
        "\n--- Climate Risk Score ---"
    )


    print(

        "Risk Score:",

        climate_risk[
            "score"
        ],

        "/ 100"

    )


    print(

        "Risk Level:",

        climate_risk[
            "risk_level"
        ]

    )


    print(
        "\n--------------------------------"
    )


    print(

        "OVERALL HAZARD RISK:",

        overall_risk

    )


    print(

        "CLIMATE RISK:",

        climate_risk[
            "risk_level"
        ]

    )


    print(
        "--------------------------------"
    )


    # ========================================================
    # SAVE LATEST ANALYSIS
    # Government uses this
    # ========================================================

    latest_analysis = {

        "latitude":
            latitude,

        "longitude":
            longitude,

        "weather_risks":
            weather_risks,

        "weather_overall_score":
            weather_overall_score,

        "weather_overall_risk":
            weather_overall_risk,

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
    # RETURN DATA TO USER FRONTEND
    # ========================================================

    return jsonify({

        "latitude":
            latitude,

        "longitude":
            longitude,

        "weather_risks":
            weather_risks,

        "weather_overall_score":
            weather_overall_score,

        "weather_overall_risk":
            weather_overall_risk,

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
# GOVERNMENT LATEST ANALYSIS
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
# GOVERNMENT REGIONAL RISK DATA
# ============================================================

@app.route("/government-risk-data")
def government_risk_data():

    region_key = request.args.get(

        "region",

        ""

    ).strip().lower()


    region = GOVERNMENT_REGIONS.get(

        region_key

    )


    if region is None:

        return jsonify({

            "available":
                False,

            "error":
                "Unknown region"

        }), 400


    latitude = region["latitude"]

    longitude = region["longitude"]


    try:

        # ====================================================
        # WEATHER
        # ====================================================

        weather = get_weather(

            latitude,

            longitude

        )


        weather_analysis = analyze_weather(



            weather



        )



        weather_risks = weather_analysis["risks"]



        weather_overall_score = weather_analysis["overall_score"]



        weather_overall_risk = weather_analysis["overall_risk"]


        # ====================================================
        # FLOOD
        # ====================================================

        flood_data = get_flood_data(

            latitude,

            longitude

        )


        flood_risk = analyze_flood(

            flood_data

        )


        # ====================================================
        # NASA EVENTS
        # ====================================================

        events_data = get_natural_events()


        natural_events = find_nearby_events(

            events_data,

            latitude,

            longitude

        )


        # ====================================================
        # OVERALL RISK
        # ====================================================

        overall_risk = calculate_overall_risk(

            weather_risks,

            flood_risk,

            natural_events

        )


        # ====================================================
        # DOMINANT HAZARD
        # ====================================================

        dominant = get_dominant_hazard(

            weather_risks,

            flood_risk

        )


        # ====================================================
        # AFFECTED AREA
        # ====================================================

        affected_area = get_affected_area(

            latitude,

            longitude,

            dominant["hazard"],

            dominant["risk"]

        )


        # ====================================================
        # POPULATION
        # ====================================================

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


        # ====================================================
        # PEOPLE AT RISK
        # ====================================================

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


        # ====================================================
        # CLIMATE RISK
        # ====================================================

        climate_risk = calculate_climate_risk(

            weather_risks,

            flood_risk,

            natural_events,

            population_data

        )


        # ====================================================
        # HAZARD LEVELS
        # ====================================================

        heat_risk = get_weather_hazard_risk(

            weather_risks,

            [

                "heat",

                "temperature"

            ]

        )


        cyclone_risk = get_weather_hazard_risk(

            weather_risks,

            [

                "cyclone",

                "wind",

                "storm"

            ]

        )


        flood_level = get_risk_level(

            flood_risk

        )


        overall_level = get_risk_level(

            overall_risk

        )


        # ====================================================
        # INFRASTRUCTURE
        # ====================================================

        infrastructure_risk = estimate_infrastructure_at_risk(

            population_data.get(

                "population",

                0

            ),

            overall_level

        )


        # ====================================================
        # RETURN REGIONAL DATA
        # ====================================================

        return jsonify({

            "available":
                True,

            "region": {

                "key":
                    region_key,

                "name":
                    region["name"],

                "latitude":
                    latitude,

                "longitude":
                    longitude

            },

            "flood_risk":
                flood_level,

            "heat_risk":
                heat_risk,

            "weather_overall_score":
                weather_overall_score,

            "weather_overall_risk":
                weather_overall_risk,

            "cyclone_risk":
                cyclone_risk,

            "overall_risk":
                overall_level,

            "people_at_risk":

                people_at_risk.get(

                    "people_at_risk",

                    0

                ),

            "infrastructure_at_risk":

                infrastructure_risk,

            "affected_radius_km":

                affected_area.get(

                    "radius_km"

                ),

            "dominant_hazard":

                affected_area.get(

                    "hazard",

                    "Climate Risk"

                ),

            "climate_risk_level":

                get_risk_level(

                    climate_risk

                ),

            "climate_risk_score":

                climate_risk.get(

                    "score",

                    0

                ),

            "natural_events_count":

                len(

                    natural_events

                    if isinstance(
                        natural_events,
                        list
                    )

                    else []

                )

        })


    except Exception as error:

        print(

            "Government regional analysis error:",

            error

        )


        return jsonify({

            "available":
                False,

            "error":
                str(error)

        }), 500


# ============================================================
# GOVERNMENT ALERTS
#
# GET  -> Read existing alerts
# POST -> Create a new alert
# ============================================================

@app.route(
    "/government-alerts",
    methods=["GET", "POST"]
)
def government_alerts_api():

    global government_alerts


    # ========================================================
    # GET ALERTS
    # ========================================================

    if request.method == "GET":

        return jsonify({

            "available":
                True,

            "alerts":
                government_alerts

        })


    # ========================================================
    # READ REQUEST DATA
    # ========================================================

    data = request.get_json(

        silent=True

    ) or {}


    region = str(

        data.get(

            "region",

            ""

        )

    ).strip()


    risk_type = str(

        data.get(

            "risk_type",

            ""

        )

    ).strip()


    severity = str(

        data.get(

            "severity",

            ""

        )

    ).strip().upper()


    message = str(

        data.get(

            "message",

            ""

        )

    ).strip()


    # ========================================================
    # VALIDATION
    # ========================================================

    if (

        not region

        or not risk_type

        or not severity

        or not message

    ):

        return jsonify({

            "success":
                False,

            "error":
                "Region, risk type, severity and message are required."

        }), 400


    if severity not in {

        "LOW",

        "MEDIUM",

        "HIGH"

    }:

        return jsonify({

            "success":
                False,

            "error":
                "Severity must be LOW, MEDIUM or HIGH."

        }), 400


    # ========================================================
    # CREATE ALERT
    # ========================================================

    alert = {

        "id":

            len(

                government_alerts

            ) + 1,

        "region":

            region,

        "risk_type":

            risk_type,

        "severity":

            severity,

        "message":

            message,

        "status":

            "PUBLISHED",

        "created_at":

            datetime.now().strftime(

                "%Y-%m-%d %H:%M:%S"

            )

    }


    # ========================================================
    # STORE ALERT
    # ========================================================

    government_alerts.insert(

        0,

        alert

    )


    # Keep the latest 20 alerts.

    government_alerts = (

        government_alerts[:20]

    )


    # ========================================================
    # RETURN CREATED ALERT
    # ========================================================

    return jsonify({

        "success":
            True,

        "alert":
            alert

    }), 201


# ============================================================
# PUBLIC ALERTS
#
# Future User Dashboard can use this endpoint.
# ============================================================

@app.route("/alerts")
def public_alerts():

    return jsonify({

        "available":
            True,

        "alerts":
            government_alerts

    })


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(

        debug=True

    )
