import re

def extract_name(response):
    while True:
        # Check if the input is a single word, assuming it's the name if so
        if response.strip().isalpha():
            return response.capitalize()

        # Regular expression to match common name introduction patterns
        match = re.search(r"\b(my name is|my name's|my names|i am|i'm|im|it's|its|call me|i'm called|im called)\s+(\w+)", response, re.IGNORECASE)

        # If we find a match, return the name part (second group)
        if match:
            return match.group(2).capitalize()

        # If neither method matches, ask the user to try again
        print("\nBot: Sorry, I couldn't quite catch that. Please could you enter your name again?\n\n")
        response = input("User: ")

# Main script logic
if __name__ == "__main__":
    # Prompt user for their name
    user_entry = input("Enter your name statement: ")
    name = extract_name(user_entry)
    print(f"Hi {name}, it's a pleasure to meet you!")  # Expected output: the user's name
