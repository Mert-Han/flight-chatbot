import nltk
import pandas as pd
import flight_data_generator
import re
from datetime import datetime, timedelta
from dateutil import parser
import date_parser
import intent_recogniser
import BookingProfile
from Flight import Flight
from name_recogniser import extract_name
import response_dict
from logger import logger
import time
import random
import string
from UserProfile import UserProfile
import user_manager

pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', 1000)  # Increase the width to avoid line wrapping

sleep_time_short = 0.5 #for short messages
sleep_time_long = 0.6 #for long messages
day_period = flight_data_generator.get_days()
display_limit = 10

# Class to quit/cancel booking halfways
class QuitException(Exception):
    pass

# like input(), but cooler (can implement custom functionality)
def safe_input(prompt=""):
    user_input = input(prompt).strip()
    user_intent = intent_recogniser.recognise(user_input.lower())
    if user_intent == 'quit':
        raise QuitException("User requested to quit.")
    elif user_input.lower() == "smiley":
        print("\n(:")
    return user_input

def within_days(date_to_check):
    # return true if none value: isn't NOT within range
    if not date_to_check:
        return True
    
    today = datetime.now()
    days_from_now = today + timedelta(day_period)
    return today <= date_to_check <= days_from_now

# Install nltk stuff if it hasn't already been downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')


# Load the flight data CSV
flight_data = pd.read_csv("flight_data.csv")

# Get list of cities
city_list_caps = flight_data_generator.get_cities()
city_list = [city.lower() for city in city_list_caps] #lowercase 
classes = ["first", "business", "economy"]


def main_booking_process(user_input, user_profile): 
    try:
        # Ensure the user profile is initialised
        if user_profile is None:
            user_profile = UserProfile(name="", preferred_date_time_format="%A, %d %B %Y", preferred_flight_class="")

        booking_profile = BookingProfile.BookingProfile()
        user_input = user_input.lower()

        origin = None
        destination = None
        departure_date_found = False
        return_date_found = False
        return_status = False

        # Check for cities
        for city in city_list:
            if f"to {city}" in user_input:
                destination = city.capitalize()
            if f"from {city}" in user_input:
                origin = city.capitalize()
            if origin and destination:
                break

        # Check for dates, and sort by earliest first - more than two dates results in None value
        extracted_dates = date_parser.extract_dates(user_input) 
        if len(extracted_dates) == 2:
            extracted_dates.sort() # Sort the dates in ascending order (earliest first)
            departure_date_found, return_date_found, return_status = True, True, True
        elif len(extracted_dates) == 1:
            departure_date_found = True
        else:
            extracted_dates = None

        # Save current information
        departure_date = None
        return_date = None

        if extracted_dates:
            if len(extracted_dates) > 0:
                departure_date = extracted_dates[0]
            if len(extracted_dates) == 2:
                return_date = extracted_dates[1]

        # Format dates according to user's preferred date-time format
        preferred_format = user_profile.preferred_date_time_format
        departure_date_str = departure_date.strftime(preferred_format) if departure_date else None
        return_date_str = return_date.strftime(preferred_format) if return_date else None

        # Check for flight class
        class_found = False
        for flight_class in classes:
            if flight_class in user_input:
                class_found = True
                break
            flight_class = None 

        # Output time
        if not within_days(departure_date) or not within_days(return_date):
            print(f"Bot: Please note, I can only provide flights for the next {day_period} days. However, you can still book", end="")
            # Reset BOTH dates - can be assumed user might not have known
            # Now they can make informed decision
            departure_date = None
            return_date = None
        else:
            print("Bot: Got it, you want to book", end="")
        
        if class_found:
            if flight_class == "economy":
                print(" an economy flight", end="") 
            if flight_class == "business":
                print(" a business flight", end="")
            if flight_class == "first":
                print(" a first class flight", end="")
        else:
            print(" a flight", end="")
        if origin:
            print(f" from {origin}", end="")
        if departure_date:
            print(f" on {departure_date_str}", end="")
        if destination:
            print(f" to {destination}", end="")
        if return_date: 
            print(f" and you want to return on {return_date_str}", end="")
        print(". Remember, at any point you can cancel your booking by typing 'quit'.", end="") 
        print("\n")
        # print("Please confirm if you would like to continue, re-e")

        # FILLING IN MISSING INFORMATION (except flight_class), saves to booking_profile
        fill_info_gaps(return_status, origin, destination, departure_date, return_date, booking_profile, user_profile)

        # PICKING A SPECIFIC FLIGHT

        # Set class preferences
        if flight_class:
            booking_profile.set_departure_flight_class(flight_class)
            booking_profile.set_return_flight_class(flight_class)

        # Confirm departure flight
        departure_flight = show_available_flights(
            booking_profile.get_origin(),
            booking_profile.get_destination(),
            booking_profile.get_departure_date(),
            is_return=False,
            flight_class=booking_profile.get_departure_flight_class(),
            user_profile=user_profile
        )

        # Save the departure flight details to the profile
        if departure_flight:
            booking_profile.set_departure_date(departure_flight.get_date())
            booking_profile.set_origin(departure_flight.get_origin())
            booking_profile.set_destination(departure_flight.get_destination())

        # Confirm return flight (if applicable)
        if booking_profile.get_return_status():
            return_flight = show_available_flights(
                booking_profile.get_destination(),
                booking_profile.get_origin(),
                booking_profile.get_return_date(),
                is_return=True,
                departure_date=booking_profile.get_departure_date(),
                flight_class=booking_profile.get_return_flight_class()
            )

            # Save the return flight details to the profile
            if return_flight:
                booking_profile.set_return_date(return_flight.get_date())

        # quit, something went wrong
        if not departure_flight:
            print("Bot: I was not able to complete your booking this time due to an invalid flight selection. Feel free to try again later.\n")
            return
        elif return_status and not return_flight:
            print("Bot: I was not able to complete your booking this time due to an invalid return flight selection. Feel free to try again later.\n")
            return

        # Get name from user
        if not user_profile.name:
            print("Bot: Before we continue, could you tell me your name? I'll use it to help store your booking.\n")
            user_profile.name = extract_name(safe_input("User: "))
            print("\n" + response_dict.get_response('greet', user_profile.name), "Here are the details for your booking.\n")
        booking_profile.set_name(user_profile.name)

        print("Your booking info:\n")
        print(f"* Origin -> {booking_profile.get_origin()}")
        print(f"* Destination -> {booking_profile.get_destination()}")
        print(f"* Departure date -> {booking_profile.get_departure_date()}")
        if booking_profile.get_return_status():
            print(f"* Return date -> {booking_profile.get_return_date()}\n")
        
        final_confirmation = intent_recogniser.recognise(safe_input(f"Bot: Would you like to confirm this booking {user_profile.name}?\n\nUser: "))
        if final_confirmation == 'yes':
            if return_status:
                confirm_booking(booking_profile, departure_flight, return_status, return_flight)
                print(f"Bot: Your booking has been saved under the name {user_profile.name}.\n")
                if flight_class:
                    user_profile.preferred_flight_class = flight_class
            else:
                confirm_booking(booking_profile, departure_flight, return_status)
            user_manager.update_user_profile(user_profile)      
        return

    except QuitException:
        print("\nBot: Exited the booking process. Your booking has been cancelled.")

# Gets user to input city (used for destination and origin)
def get_city():
    city_input = safe_input("User: ").lower()
    print()

    city_found = False
    while not city_found:
        for city in city_list:
            if city in city_input:
                city_found = True
                return city.capitalize()

        print("Bot: Sorry, the city you entered isn't in my database. Would you like a list of the available cities?\n")
        intent = intent_recogniser.recognise(safe_input("User: "))
        print()

        # Remind user of cities available
        if intent == 'yes':
            for city in city_list_caps:
                print(f"* {city}")
            print("\nBot: These are all the cities available in my database, please enter the one you would like to depart from.\n")
        else:
            print("Bot: Please enter which city you would like to depart from.\n")

        city_input = safe_input("User: ").lower()

def fill_info_gaps(return_flight, origin, destination, departure_date, return_date, booking_profile, user_profile):

    # Check if return flight
    if not return_flight:
        intent = intent_recogniser.recognise(safe_input("Bot: Is that to be a return flight?\n\nUser: "))
        print()
        if intent == 'yes':
            return_flight = True
    else:
        print("\n") 

    # If return flight but no return date, get date
    if return_flight and not return_date: 
        if origin:
            print(f"Bot: Which day would you like to return to {origin}?\n")
        else:
            print(f"Bot: Please enter which day you would like to return.\n")

        while True:
            return_input = safe_input("User: ")
            print()
            return_date_unparsed = date_parser.extract_dates(return_input) 

            if len(return_date_unparsed) == 1: # Check only one date entered
                return_date = return_date_unparsed[0]

                if not within_days(return_date):
                    print(f"Bot: Please note, I can only provide flights for the next {day_period} days. Please enter a new date.\n")
                    continue

                # If we have depart date, check its before return
                if departure_date:
                    if return_date < departure_date: # Ensure return date is after the first date
                        print(f"Bot: The return date must be after the departure date ({departure_date.strftime(user_profile.preferred_date_time_format)}). Please try again.\n")
                        continue
                
                print(f"Bot: Got it, you want to return on {return_date.strftime(user_profile.preferred_date_time_format)}.\n")
                break
                
            else:
                print("Bot: I couldn't understand that date. Please try again.\n")

    # Get departure date if none entered
    if not departure_date:
        if origin:
            print(f"Bot: Please enter the day you would like to depart from {origin}.\n")
        else:
            print(f"Bot: Please enter the day you would like to depart.\n")
        
        while True:
            departure_input = safe_input("User: ")
            print()
            departure_date_unparsed = date_parser.extract_dates(departure_input) 

            if len(departure_date_unparsed) == 1: # Check only one date entered
                departure_date = departure_date_unparsed[0]

                if not within_days(departure_date):
                    print(f"Bot: Please note, I can only provide flights for the next {day_period} days. Please enter a new date.\n")
                    continue

                # if return, ensure departure comes first
                if return_flight:
                    if departure_date > return_date: 
                        print(f"Bot: The departure date must be before the return date ({return_date.strftime(user_profile.preferred_date_time_format)}). Please try again.\n")
                        continue
                    
                # Success!
                print(f"Bot: Got it, you want to depart on {departure_date.strftime(user_profile.preferred_date_time_format)}\n")
                break
            else:
                print("Bot: I couldn't understand that date. Please try again.\n")

    # Check origin, destination
    if not origin: 
        print(f"Bot: Where would you like to depart from?\n")
        origin = get_city()
        print(f"Bot: Noted, you're leaving from {origin}.\n")
        
    if not destination: 
        print(f"Bot: Where would you like to arrive?\n")
        destination = get_city()
        print(f"Bot: Noted, you're leaving from {destination}.\n")
    # print("!!!!! return date = ", return_date)

    # Save new information to booking_profile
    booking_profile.set_origin(origin)
    booking_profile.set_destination(destination)
    booking_profile.set_departure_date(departure_date)
    booking_profile.set_return_date(return_date)
    booking_profile.set_return_status(return_flight)

    print("Bot: Alright, we're almost done. Now you just need to select which flight(s) you prefer. \n")
    return
    
def show_available_flights(
    departure_city, destination_city, preferred_date, is_return=False, departure_date=None, flight_class=None, user_profile=None
):
    """
    Displays available flights and allows the user to select one. 
    Handles departure and return flights separately and ensures return flights don't precede departures.


    departure_city: Departure city for the flight.
    destination_city: Destination city for the flight.
    preferred_date: Preferred date for the flight (YYYY-MM-DD).
    is_return: Flag to indicate if this is a return flight.
    departure_date: Departure date for the original flight (used for validation).
    flight_class: Preferred flight class (optional).
    """

    flight_df = pd.read_csv("flight_data.csv")
    matching_flights = pd.DataFrame()  # Initialise as empty DataFrame

    if user_profile is None:
        user_profile = UserProfile(name="", preferred_date_time_format="%Y-%m-%d", preferred_flight_class="")

    # Validate and convert dates
    if preferred_date is not None:
        preferred_date = pd.to_datetime(preferred_date, format="%Y-%m-%d", errors="coerce")
    if departure_date is not None:
        departure_date = pd.to_datetime(departure_date, format="%Y-%m-%d", errors="coerce")


    # Validate preferred_date
    if preferred_date is None:
        print("Bot: Preferred date is missing. Cannot search for flights.")
        return None
    
    # Convert dates in the DataFrame to datetime
    flight_df["departure_date"] = pd.to_datetime(flight_df["departure_date"], format="%Y-%m-%d", errors="coerce")

    # Determine the flight class to filter
    if not flight_class and user_profile and user_profile.preferred_flight_class:
        flight_class = user_profile.preferred_flight_class
        # print(f"Bot: Applying your preferred flight class: {flight_class}.\n")
 
    new_return = False #flag. if departure set to after return, we skip to finding a range of flights
    if is_return:
        if departure_date is None:
            print("\nBot: Departure date is missing. Cannot search for return flights.")
            return None

        # Adjust preferred_date if it comes before departure_date
        if preferred_date is None or preferred_date <= departure_date:
            preferred_date = departure_date + timedelta(days=1)
            print("Bot: Your selected departure date comes after the original return date you set. "
              "I'll adjust my search to show flights after your departure date.\n")
            new_return = True

    
    logger.debug(f"preferred date = {preferred_date}")

    print(f"Bot: Currently searching for flights from {departure_city} to {destination_city}...\n")
    
    if not new_return:
        # Outbound flight logic
        if not is_return:
            matching_flights = flight_df[
                (flight_df["departure_city"].str.lower() == departure_city.lower()) &
                (flight_df["arrival_city"].str.lower() == destination_city.lower()) &
                (flight_df["departure_date"] == preferred_date)
            ]
        # Return flight logic
        else:
            matching_flights = flight_df[
                (flight_df["departure_city"].str.lower() == destination_city.lower()) &
                (flight_df["arrival_city"].str.lower() == departure_city.lower()) &
                (flight_df["departure_date"] == preferred_date)
            ]
        

        # Ensure 'flight_class' is a valid string
        if not isinstance(flight_class, str):
            flight_class = ""  # Default to an empty string if None or NaN

        # Ensure 'flight_class' column is sanitised
        if "flight_class" in matching_flights.columns:
            matching_flights.loc[:, "flight_class"] = (
            matching_flights["flight_class"]
            .fillna("")  # Replace NaN with an empty string
            .astype(str)  # Ensure all values are strings
            .str.strip()  # Remove leading/trailing spaces
            .str.lower()  # Convert to lowercase
        )

        # Compare with the provided flight class
        matching_flights = matching_flights[matching_flights["flight_class"] == flight_class.lower()]

        # Ask user if they want to disable the filter
        if flight_class:
            disable_filter = safe_input(f"Bot: My default behaviour is to sort by your preferred class, which as "
                                        f"I understand it is {flight_class} class flights. "
                                        f"Would you like to see all flights on this day instead? (yes/no)\n\nUser: ").strip().lower()
            print()
            if disable_filter == "yes":
                matching_flights = flight_df[
                    (flight_df["departure_city"].str.lower() == departure_city.lower()) &
                    (flight_df["arrival_city"].str.lower() == destination_city.lower()) &
                    (flight_df["departure_date"] == preferred_date)
                ]


    # HANDLING NO MATCHES
    # print(f"is return = {is_return}")
    alt_flights = False
    if matching_flights.empty:
        alt_flights = True
        
        # Expand search within a 30-day limit
        search_end_date = datetime.now() + timedelta(day_period)
        # If return flight, start return search from after departure
        if is_return:
            search_start_date = departure_date + timedelta(days=1)
        else:
            search_start_date = datetime.now()

        logger.debug(f"search start = {search_start_date}\nsearch end = {search_end_date}")

        # Updated loop condition to prevent infinite loops
        while matching_flights.empty and search_start_date <= search_end_date:
            matching_flights = flight_df[
                (flight_df["departure_city"].str.lower() == departure_city.lower()) &
                (flight_df["arrival_city"].str.lower() == destination_city.lower()) &
                (flight_df["departure_date"].between(search_start_date, search_end_date))
            ]

            if flight_class:
                matching_flights = matching_flights[
                    matching_flights["flight_class"].str.lower() == flight_class.lower()
                ]
            
            # Ensure return is after departure (for return flights)
            if is_return:
                matching_flights = matching_flights[
                    (matching_flights["departure_date"] > departure_date)  
                ]

            # Update search range to prevent infinite loop
            search_start_date += timedelta(days=1)

    # print(matching_flights)
    # Still no flights found
    time.sleep(sleep_time_long)
    if matching_flights.empty:
        print(f"Bot: Sorry, I couldn't find any {flight_class or 'flights'} between {departure_city} and {destination_city} within {day_period} days.\n")
        return None

    # Found flights, but they're not on the same day
    elif not matching_flights.empty and alt_flights:
        print(f"Bot: I couldn't find any flights with your requirements on {preferred_date.strftime(user_profile.preferred_date_time_format)}...\n")
        time.sleep(sleep_time_long)
        print(f"Bot: ...but I was able to find some alternative {departure_city} to {destination_city} flights:\n")
    # Found flights on the same day
    else:
        print(f"Bot: Here are the available flights on {preferred_date.strftime(user_profile.preferred_date_time_format)}:\n")
    time.sleep(sleep_time_long)


    # Display limited entries with pagination
    current_start_index = 0  # Start index for slicing the DataFrame
    selected_flight = None
    # print(flight_class)

    while True:
        # Display the current slice of matching_flights
        current_slice = matching_flights.iloc[current_start_index:current_start_index + display_limit]
        
        # Check if there are entries to display
        if current_slice.empty:
            print("Bot: No more flights to show. Please select an available flight ID or type 'go back' to view previous flights.\n")
            user_input = safe_input("User: ").lower()
            if user_input == "go back" and current_start_index > 0:
                current_start_index = max(0, current_start_index - display_limit)  # Move to the previous slice
                continue
            else:
                print("Bot: Invalid input. Enter a valid flight ID or type 'go back' if you'd like to view previous options.")
            continue

        for idx, flight in current_slice.iterrows():
            print(
                f"[*] ID: {idx}, {flight['departure_date'].strftime(user_profile.preferred_date_time_format)} "
                f"({flight['flight_class']}, £{flight['flight_cost']}, {flight['flight_duration_hours']} hours)"
            )
        print(f"\n(Currently showing flights {current_start_index + 1} to {current_start_index + len(current_slice)} of {len(matching_flights)}.)\n")
        
        # Ask user for input
        options = []
        if current_start_index > 0:
            options.append("'go back'")
        if current_start_index + display_limit < len(matching_flights):
            options.append("'show more'")
        options_str = " or ".join(options)

        time.sleep(sleep_time_long)
        user_input = safe_input(f"Bot: Please enter the ID of the flight you'd like to select{f', or type {options_str}' if options else ''}. "
                                f"Or type 'quit' to quit. \n\nUser: ").lower()
        print()

        if user_input == "show more" and current_start_index + display_limit < len(matching_flights):
            current_start_index += display_limit  # Move to the next slice
            continue
        elif user_input == "go back" and current_start_index > 0:
            current_start_index = max(0, current_start_index - display_limit)  # Move to the previous slice
            continue
        try:
            # Validate the user's choice
            flight_id = int(user_input)
            if flight_id in current_slice.index:
                selected_flight = matching_flights.loc[flight_id]
                print(f"\nBot: You've selected the flight from {selected_flight['departure_city']} to {selected_flight['arrival_city']} "
                    f"on {selected_flight['departure_date'].strftime(user_profile.preferred_date_time_format)}.\n")
                break
            else:
                print("Bot: Invalid selection. Please choose a valid flight ID from the displayed options.\n")
        except ValueError:
            print("\nBot: Please enter a valid number or a valid command ('go back', 'show more', 'quit').\n")


    # Return the selected flight as a Flight object
    return Flight(
        date=selected_flight["departure_date"].strftime("%Y-%m-%d"),
        origin=selected_flight["departure_city"],
        destination=selected_flight["arrival_city"],
        flight_class=selected_flight["flight_class"]
    )

def generate_booking_id():
    """Generate a simple alphanumeric booking ID."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def confirm_booking(booking_profile, departure_flight, return_status, return_flight=None):
    """
    Appends the booking details to a CSV file. Each flight is stored as a separate row.
    
    Parameters:
    - booking_profile: The BookingProfile object.
    - departure_flight: The Flight object for the departure flight.
    - return_flight: The Flight object for the return flight (if applicable).
    """
    # Define the file name for storing confirmed bookings
    filename = "resources/confirmed_bookings.csv"
    
    # Generate a simplified booking ID for linking departure and return flights
    booking_id = generate_booking_id()
    
    # Prepare rows for departure and return flights
    rows = [
        {
            "Booking ID": booking_id,
            "Name": booking_profile.get_name(),
            "Flight Type": "Departure",
            "Date": departure_flight.get_date(),
            "Origin": departure_flight.get_origin(),
            "Destination": departure_flight.get_destination(),
            "Class": departure_flight.get_flight_class()
        }
    ]
    
    # Add return flight details if applicable
    if return_status:
        rows.append({
            "Booking ID": booking_id,
            "Name": booking_profile.get_name(),
            "Flight Type": "Return",
            "Date": return_flight.get_date(),
            "Origin": return_flight.get_origin(),
            "Destination": return_flight.get_destination(),
            "Class": return_flight.get_flight_class()
        })
    
    # Convert rows to a DataFrame
    booking_df = pd.DataFrame(rows)
    
    # Append to the CSV file
    try:
        # Check if the file exists and write accordingly
        with open(filename, 'a') as file:
            if file.tell() == 0:  # File is empty, write header
                booking_df.to_csv(file, index=False)
            else:  # Append without writing header
                booking_df.to_csv(file, index=False, header=False)
        
        print(f"\nBot: Your booking has been successfully confirmed, {booking_profile.get_name()}! "
              f"Make sure to keep a note of your booking ID, in case you want to view or cancel your booking. \n\nBooking ID: {booking_id}\n")
        time.sleep(sleep_time_long)
    except Exception as e:
        print(f"\nBot: There was an error saving your booking: {e}\n")

def print_cities():
    for city in city_list_caps:
        print(f"* {city}")



user_inputs = [
    "i want to book a flight to london",
    "I want to book a flight to singapore from london in 30 days and return in 31 days",
    "Get me an economy flight from london to singapore from the 10th to the 20th",
    "I want to fly to Singapore in 7 days",
    "I want to go to London on the 19th",
    "I want to travel on the 19th to singapore from london and come back on the 20th",
    "Can I book an economy flight tomorrow?",
    "I need a flight today",
    "I want to fly on the 28th"
]

# # For testing
# for input_text in user_inputs:
#     print(f"\nUser: {input_text}\n")
#     user_name = None
#     main_booking_process(input_text, user_name)
#     print("\n")
