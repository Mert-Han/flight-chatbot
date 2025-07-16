import pandas as pd
import random
from datetime import datetime, timedelta
from itertools import permutations

# Dictionary of locations: countries as keys, cities as values
locations = {
    "USA": ["New York City", "Los Angeles"],
    "United Kingdom": ["London"],
    "France": ["Paris"],
    "Japan": ["Tokyo"],
    "United Arab Emirates": ["Dubai"],
    "Australia": ["Sydney"],
    "Italy": ["Rome"],
    "Thailand": ["Bangkok"],
    "Singapore": ["Singapore"]
}

days = 60

def get_days():
    return days

def get_locations():
    return locations

def get_cities():
    city_list = []
    for country, cities in locations.items():
        city_list.extend(cities)
    return city_list

# Function to generate a random flight cost based on class
def generate_random_cost(flight_class):
    if flight_class == "Economy":
        return round(random.uniform(100, 300), 2)  # Economy: £100 - 300
    elif flight_class == "Business":
        return round(random.uniform(400, 700), 2)  # Business: £400 - 700
    elif flight_class == "First":
        return round(random.uniform(800, 1200), 2)  # First: £800 - 1200

# Function to create flight data for all city combinations
def generate_flight_data():
    today = datetime.now()
    flight_data = []
    cities = get_cities()

    # Generate data for the next 30 days
    for day_offset in range(days):
        departure_date = today + timedelta(days=day_offset)

        # Generate flights for all city combinations (including both directions)
        for departure_city, arrival_city in permutations(cities, 2):
            flight_duration = random.randint(2, 12)  # Flight duration in hours
            arrival_date = departure_date + timedelta(hours=flight_duration)
            flight_class = random.choice(["Economy", "Business", "First"])
            flight_cost = generate_random_cost(flight_class)

            # Find countries for the cities
            departure_country = next(country for country, city_list in locations.items() if departure_city in city_list)
            arrival_country = next(country for country, city_list in locations.items() if arrival_city in city_list)

            # Append flight data
            flight_data.append({
                "departure_date": departure_date.strftime("%Y-%m-%d"),
                "arrival_date": arrival_date.strftime("%Y-%m-%d"),
                "flight_duration_hours": flight_duration,
                "flight_cost": flight_cost,
                "flight_class": flight_class,
                "departure_city": departure_city,
                "departure_country": departure_country,
                "arrival_city": arrival_city,
                "arrival_country": arrival_country
            })

    return flight_data

# Create DataFrame from the flight data
flight_data = generate_flight_data()
flight_df = pd.DataFrame(flight_data)

# Write to CSV (this will overwrite the file each time)
flight_df.to_csv("flight_data.csv", index=False)
