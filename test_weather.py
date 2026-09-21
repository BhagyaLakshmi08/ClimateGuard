from services.population_service import (
    get_population_in_area
)


# Test location
latitude = 16.4578548
longitude = 80.5344060


# Test affected-area radius
radius = 5


population_data = get_population_in_area(
    latitude,
    longitude,
    radius
)


print("\n======================================")
print("CLIMATEGUARD POPULATION ANALYSIS")
print("======================================")


print(
    "Location:",
    population_data["latitude"],
    population_data["longitude"]
)


print(
    "Affected Radius:",
    population_data["radius_km"],
    "km"
)


print(
    "Population Data Year:",
    population_data["data_year"]
)


print(
    "Estimated People in Area:",
    population_data["population"]
)


print("======================================")