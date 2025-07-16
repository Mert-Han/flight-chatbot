# flight-chatbot
A Python-based chatbot for booking, viewing, and managing flight reservations. Designed to handle natural language input, dynamic parsing, and conversational interaction, this project explores practical human-AI dialogue for transactional tasks.

## Features

- **Book a flight** — Book single or return flights between available cities with optional flight class selection.
- **View bookings** — Retrieve existing bookings by name or reference number.
- **Cancel bookings** — Cancel an existing booking with confirmation.
- **View available cities** — Check the list of destinations currently supported.
- **General conversation** — Engage in basic small talk and ask about available commands.
- **Check date and time** — Get the current system date and time.

## System Architecture

- **Chatbot Controller (`Chatbot.py`)**  
  Coordinates user input, manages conversation flow, and routes commands to relevant modules.
  
- **Intent Recognition (`intent_recogniser.py`)**  
  Uses a dictionary-based approach combined with TF-IDF and cosine similarity to match user inputs against known intents and question-answer pairs.

- **Booking Workflow (`booking_process.py`)**  
  Handles flight booking tasks, including input validation, confirmation, and information gathering using dynamic parsing and user prompts.

- **Date Parsing (`date_parser.py`)**  
  Supports flexible date formats, recognising both natural language inputs (e.g. "next Friday") and specific dates.

- **Profiles and State Management**  
  - `UserProfile` stores individual user preferences and persists them between sessions.
  - `BookingProfile` keeps track of booking data during a session.
  - `Flight` represents a single flight booking.

## Data Storage

All data is stored in CSV format for simplicity and human readability:
- `confirmed_bookings.csv` — Records of confirmed bookings.
- `flight_data.csv` — Available flight listings.
- `user_profiles.csv` — User preferences and details.
- `QAdataset.csv` — Frequently asked questions and predefined answers.

## Conversational Design

- **Adaptability** — Supports flexible date input and dynamically requests missing information.
- **Personalisation** — Remembers user preferences and greets returning users.
- **Prompt Design** — Uses pagination for large result sets and provides clear command options.
- **Error Handling** — Offers guidance when inputs are unclear or invalid, and allows users to cancel operations at any time.
- **Discoverability** — Presents available commands on start-up and after periods of inactivity.

## Evaluation and Testing

Performance and usability were validated through user testing and profiling.  

Key findings:
- The date parser reliably handled a variety of input styles.
- Intent recognition was effective but identified as a performance bottleneck due to repeated text processing.
- User feedback highlighted strong discoverability and conversational flow, though improvements could be made to booking modifications and data consistency.

## Future Improvements

- Introduce more flexible intent matching using semantic models.
- Allow users to modify bookings before final confirmation.
- Replace random flight data with a consistent or real-world data source.

## Contact <a id="contact"></a>

*Mert-Han H* – `contact.merthanharry@gmail.com` 
