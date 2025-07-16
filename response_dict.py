import random
from datetime import datetime
import time

responses = {
    'greet': ['Hi {name}!', 'Hello {name}!', 'Hiya {name}!', 'Greetings {name}!', 'Saluations {name}!', 'I hope you\'re doing well {name}!'],
    'farewell': ['Bye!', 'Goodbye!', 'Farewell', 'Hope to see you again soon!', 'I guess this is it then... goodbye.', 'I suppose all good things must come to an end.'],
    
    # 'capability': ['Currently, I can greet users and remember their names. And answer this question. Duh.'],
    'emotion': ['I\'m doing pretty well! Although I am a bot. Such is life.'],

    'error': ["Sorry, something went wrong."],

    'intro': [
        "where the waves are always gnarly and the flights are smooth.",
        "where the surf\'s up and so are the travel deals.",
        "where you catch the best waves and the cheapest flights.",
        "where your next adventure is just a short board ride away.",
        "where your next trip is just a wave away, dude!"
    ]
}

def explain_capabilities():
    """
    Provide a detailed explanation of the chatbot's capabilities, printing
    each paragraph separately with pauses between them.
    """
    paragraphs = [
        "I am a virtual assistant designed to help you with the following:\n",
        "1. Flight Booking:\n"
        "   - Book single or return flights between predefined cities.\n"
        "   - Specify multiple details in your initial prompt, such as:\n"
        "       * Departure and destination cities (e.g., 'Book a flight from London to Paris').\n"
        "       * Travel dates (e.g., 'next Monday' or 'on December 25').\n"
        "       * Preferred flight class (e.g., economy, business, or first class).\n"
        "   - Dynamically detect and fill in any missing details by asking follow-up questions.\n",

        "2. Booking Management:\n"
        "   - View your current bookings using a reference number or name.\n"
        "   - Cancel existing bookings with ease.\n",
        "3. Flight Information:\n"
        "   - View all available flight destinations and schedules.",
        "4. General Assistance:\n"
        "   - Ask me general questions or have a quick chat.\n"
        "   - Learn more about my features by asking, 'What can you do?\n'",
        "5. Date and Time:\n"
        "   - Check the current date and time at any point.\n",
        "You can combine details in a single message. For example:\n"
        "- 'Book a flight from New York to London next Thursday in business class.'\n"
        "- 'Find flights to Paris this Friday and return next Sunday in economy class.'\n"

        "\nHopefully this helps! Let me know if you'd like to do any of these."
    ]
    
    for paragraph in paragraphs:
        print(paragraph)
        time.sleep(0.6)  # Pause for 2 seconds before printing the next paragraph


def get_time_based_greeting():
    now = datetime.now()
    current_hour = now.hour
    if current_hour < 12:
        greeting = "Good morning"
    elif current_hour < 18:
        greeting = "Good afternoon"
    elif current_hour < 21:
        greeting = "Good evening"
    else:
        greeting = "Good night"
    current_time = now.strftime("%A, %d %B %Y, %I:%M %p")
    return f"{greeting}! It's currently {current_time}."

# no_bot = True returns response without Bot: prefix
def get_response(intent, name=None, no_bot=False, **kwargs):
    response = random.choice(responses[intent])

    if name: 
        response = response.format(name=name)
    if kwargs:
        response = response.format(**kwargs)
    
    if no_bot:
        return response
    else:
        return f"Bot: " + response
        