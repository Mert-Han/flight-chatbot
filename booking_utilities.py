import pandas as pd
import os
import time

# Filepath for the confirmed bookings CSV
FILENAME = "resources/confirmed_bookings.csv"
sleep_time_long = 0.6  # for long messages

def display_flights(booking_id):
    if not os.path.exists(FILENAME):
        print("Bot: No bookings found. The file is missing. Now exiting the viewing process. "
              "Is there anything else I can help you with?\n")
        return None

    # Load the bookings
    bookings = pd.read_csv(FILENAME)

    # Filter flights by Booking ID
    associated_flights = bookings[bookings["Booking ID"] == booking_id]

    if associated_flights.empty:
        print(f"Bot: No flights found for Booking ID: {booking_id}, exiting the viewing process. "
              "Is there anything else I can help you with?\n")
        return None

    # Display the flights
    print(f"Bot: Here are the flights associated with Booking ID: {booking_id}.\n")
    print(associated_flights.to_string(index=False))

    return associated_flights

def display_flights_by_name(name):
    if not os.path.exists(FILENAME):
        print("Bot: No bookings found. The file is missing.\n")
        return None

    # Load the bookings
    bookings = pd.read_csv(FILENAME)

    # Filter flights by Name
    associated_flights = bookings[bookings["Name"].str.lower() == name.lower()]

    if associated_flights.empty:
        print(f"Bot: No flights found for the name: {name}.\n")
        return None

    # Display the flights
    print(f"Bot: Here are the flights associated with the name: {name}.\n")
    print(associated_flights.to_string(index=False))

    return associated_flights

def remove_booking(booking_id):
    """
    Remove all flights associated with a given booking ID.
    """
    if not os.path.exists(FILENAME):
        print("Bot: No bookings found. The file is missing.\n")
        return

    # Load the bookings
    bookings = pd.read_csv(FILENAME)

    # Check if the booking ID exists
    if booking_id not in bookings["Booking ID"].values:
        print(f"Bot: No bookings found for Booking ID: {booking_id}.")
        return

    # Remove flights associated with the booking ID
    updated_bookings = bookings[bookings["Booking ID"] != booking_id]

    # Save the updated bookings back to the file
    updated_bookings.to_csv(FILENAME, index=False)

    print(f"Bot: Booking ID: {booking_id} has been successfully canceled.\n")

def manage_booking():
    """
    Prompt the user to input a Booking ID or name, view associated flights,
    and choose to either continue or cancel a specific booking.
    """
    if not os.path.exists(FILENAME):
        print("Bot: No bookings found. The file is missing.")
        return

    # Prompt user for a Booking ID or Name
    identifier = input("Bot: Please enter a Booking ID or the name associated with the booking you would like to view or cancel.\n\nUser: ").strip()
    print()
    time.sleep(sleep_time_long)

    # Attempt to display flights by Booking ID
    flights = display_flights(identifier)

    # If no flights found by Booking ID, attempt by Name
    if flights is None:
        print("Bot: No bookings found for the provided Booking ID. Searching by name instead...\n")
        flights_by_name = display_flights_by_name(identifier)
        if flights_by_name is None:
            print("Bot: No bookings found for the provided name either. Exiting the process.\n")
            return

        # If flights are found by name, prompt for a Booking ID
        while True:
            booking_id = input("Bot: Please enter the Booking ID of the flight(s) you want to manage from the list above.\n\nUser: ").strip().upper()
            print()
            flights = display_flights(booking_id)
            if flights is not None:
                break
            print("Bot: Invalid Booking ID. Please try again or type 'exit' to abort.\n")
            if input("User: ").strip().lower() == 'exit':
                print("Bot: Exiting the process.\n")
                return
    else:
        # If flights were found using the initial Booking ID, assign it to booking_id
        booking_id = identifier

    time.sleep(sleep_time_long)
    # Prompt user to continue or cancel the booking
    while True:
        user_input = input("\nBot: Would you like to continue or cancel this booking? (type 'continue' or 'cancel').\n\nUser: ").strip().lower()
        print()
        if user_input == "cancel":
            remove_booking(booking_id)  # Use the actual booking_id
            break
        elif user_input == "continue":
            print(f"Bot: You have chosen to continue with Booking ID: {booking_id}. No changes were made.\n")
            break
        else:
            print("Bot: Invalid input. Please type 'continue' or 'cancel'.\n")


if __name__ == "__main__":
    manage_booking()
