import intent_recogniser
import name_recogniser
import response_dict
import booking_process
import booking_utilities
from user_manager import get_user_profile, add_user_profile, update_user_profile
import time
from datetime import datetime
import user_manager
from UserProfile import UserProfile
import pandas as pd
import time
import select
import sys

interval_long = 0.6

def print_answer(intent, qa_csv_path):
    # Extract the QuestionID (remove the "print_" prefix)
    question_id = intent[len("print_"):]    
    # Load the QAdataset
    data = pd.read_csv(qa_csv_path, usecols=["QuestionID", "Answer"])
    # Search for the corresponding answer using the QuestionID
    answer = data.loc[data["QuestionID"] == question_id, "Answer"].values
    if answer.size > 0:
        # Print the answer if found
        print(f"Bot: {answer[0]}")
    else:
        # If no matching question is found
        print(f"Bot: No answer found for {question_id}.")

class Chatbot:
    def __init__(self):
        self.qa_csv_path = "resources/QAdataset.csv"
        self.current_user = None
        user_manager.initialise_user_profiles_csv()

    def handle_input(self, user_input, state):

        # Recognise intent
        intent = intent_recogniser.recognise(user_input)

        # Print QA response
        if intent.startswith("print_"):
            print_answer(intent, self.qa_csv_path)

        # Handle specific intents
        elif intent == "greet":
            self.handle_greet()
        elif intent == "farewell":
            print(response_dict.get_response('farewell'))
            state = False
        elif intent == "capability":
            response_dict.explain_capabilities()
        elif intent == "emotion":
            print(response_dict.get_response('emotion'))
        elif intent == "say name":
            self.handle_say_name()
        elif intent == "booking":
            self.handle_booking(user_input)
        elif intent == "view":
            booking_utilities.manage_booking()
        elif intent == 'cities':
            booking_process.print_cities()
            time.sleep(interval_long)
            print("\nThese are the cities available in my database. Let me know if you'd like to book a flight.")
        elif intent == 'time':
            self.handle_time()
        elif intent == 'changeformat':
            self.handle_changeformat()
        elif intent == 'module':
            print("Personally I LOVE COMP3074, Human AI interaction is my favourite. I may be biased.")
        elif intent == "none_found":
            if user_input:
                print("Sorry, I wasn't able to parse your response. Please could you be more specific?")
        return state

    def handle_greet(self, prompt_for_name=True, silent=False):
        if not self.current_user:  # If no user profile exists
            if prompt_for_name and not silent:
                print("Bot: Hello! What should I call you?\n")
            
            while not self.current_user:  # Loop until a valid name is captured
                user_input = input("User: ")
                user_name = name_recogniser.extract_name(user_input)  # Use your extract_name function
                if user_name:
                    existing_user = get_user_profile(user_name)
                    if existing_user:
                        self.current_user = existing_user
                        print(f"\nBot: Welcome back, {self.current_user.name}! I've loaded your preferences.")
                    else:
                        self.current_user = add_user_profile(user_name)
                        print(f"\nBot: Nice to meet you, {self.current_user.name}! I've created a new profile for you.")
                else:
                    print("Bot: Sorry, I couldn't catch your name. Could you try again?")
        else:  # If user profile already exists
            if not silent:
                print(f"Bot: I hope you're doing well, {self.current_user.name}!")



    def handle_time(self):
        now = datetime.now()
        if not self.current_user:
            # Default to natural language format if no user profile is set
            print(f"Bot: Today is {now.strftime('%A, %d %B %Y')}, and the time is {now.strftime('%I:%M %p')}.")
        else:
            # Use the user's preferred format
            preferred_format = self.current_user.preferred_date_time_format
            print(f"Bot: {now.strftime(preferred_format)}")

    def handle_booking(self, user_input):
        booking_process.main_booking_process(user_input, self.current_user)

    def handle_say_name(self):
        if not self.current_user:
            print("Bot: I'm afraid I don't know your name yet. Could you tell me?\n")
            self.handle_greet(prompt_for_name=True, silent=True)
        else:
            print(f"Bot: You're {self.current_user.name}!")


    def update_user_preferences(self):
        if self.current_user:
            update_user_profile(self.current_user)

    def handle_changeformat(self):
        """
        Handles the 'changeformat' intent by prompting the user to select a date format.
        Updates the user's profile if it exists, or creates a new one if necessary.
        """
        natural_format = "%A, %d %B %Y"  # Natural language format
        numeric_format = "%Y-%m-%d"  # Numeric format

        # Display options to the user
        print("Bot: Please choose your preferred date format:")
        print(f"1. Natural language (e.g., {datetime.now().strftime(natural_format)})")
        print(f"2. Numeric format (e.g., {datetime.now().strftime(numeric_format)})")
        print()

        # Get user choice
        choice = input("User: ").strip()
        print()

        # Determine the selected format
        if choice == "1":
            selected_format = natural_format
            print("Bot: You have selected the natural language format.\n")
        elif choice == "2":
            selected_format = numeric_format
            print("Bot: You have selected the numeric format.")
        else:
            print("Bot: Invalid choice. Returning to the main menu.")
            return

        # Check if the current user exists
        if self.current_user:
            # Update existing profile
            self.current_user.preferred_date_time_format = selected_format
            update_user_profile(self.current_user)
            print(f"Bot: Your profile has been updated with the new date format preference, {self.current_user.name}.")
        else:
            # If no user is set, prompt for their name
            print("Bot: I don't know your name yet. Please provide your name to save your preferences.\n")
            user_name = input("User: ").strip()
            print()

            # Check if a profile exists for this name
            existing_user = get_user_profile(user_name)
            if existing_user:
                # Update the existing profile
                existing_user.preferred_date_time_format = selected_format
                update_user_profile(existing_user)
                self.current_user = existing_user
                print(f"Bot: Your existing profile has been updated with the new date format preference, {user_name}.")
            else:
                # Create a new profile
                self.current_user = add_user_profile(user_name)
                self.current_user.preferred_date_time_format = selected_format
                update_user_profile(self.current_user)
                print(f"Bot: A new profile has been created for you, {user_name}, with the selected date format.")


def get_user_input_with_timeout(prompt, timeout=90, inactivity_message="\nBot: Are you still there? If you like, you can ask 'what can you do' for more details about my functionality."):
    """
    Prompt the user for input with a timeout. If no input is provided within the timeout,
    an inactivity message is displayed, but not consecutively.
    """
    # Use a static variable to track if the inactivity message was displayed last time
    if not hasattr(get_user_input_with_timeout, "last_was_timeout"):
        get_user_input_with_timeout.last_was_timeout = False

    # Print the prompt only if it hasn't been shown after an inactivity message
    if not get_user_input_with_timeout.last_was_timeout:
        print(prompt, end="", flush=True)

    # Use select to wait for input with a timeout
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        user_input = sys.stdin.readline().strip()
        get_user_input_with_timeout.last_was_timeout = False  # Reset flag
        return user_input
    else:
        if not get_user_input_with_timeout.last_was_timeout:
            print(f"\n{inactivity_message}\n")
            get_user_input_with_timeout.last_was_timeout = True  # Set flag to prevent consecutive messages
        return None



if __name__ == "__main__":
    # Greet the user with time-based greeting and current date/time
    time_based_greeting = response_dict.get_time_based_greeting()
    print(f"\nBot: {time_based_greeting}", end=" ")
    print("Welcome to Mert's Travel Agency,", response_dict.get_response('intro', no_bot=True) + "\n")
    time.sleep(interval_long)
    print("Currently, you can:\n\n"
          "[*] Book a flight\n"
          "[*] View your current bookings\n"
          "[*] Cancel bookings\n"
          "[*] View available cities for flights\n"
          "[*] Have a quick chat\n"
          "[*] Get the current date and time\n"
          "[*] Change date and time format\n"
          "[*] Or say bye to end the conversation\n"
          "\nLet me know if any of these options interest you, and feel free to ask more about my functionality.\n")

    # Create an instance of Chatbot
    chatbot = Chatbot()

    # Start conversation loop
    state = True
    while state:
        user_input = get_user_input_with_timeout("User: ")
        if user_input is None:
            # Skip processing if no input is provided
            continue
        print("")
        # Call handle_input on chatbot instance
        state = chatbot.handle_input(user_input, state)
        print("")

