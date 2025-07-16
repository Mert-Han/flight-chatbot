import pandas as pd
import os
from UserProfile import UserProfile

def initialise_user_profiles_csv():
    if not os.path.exists("user_profiles.csv"):
        df = pd.DataFrame(columns=["Name", "PreferredDateTimeFormat", "PreferredFlightClass"])
        df["Name"] = df["Name"].astype(str)
        df["PreferredDateTimeFormat"] = df["PreferredDateTimeFormat"].astype(str)
        df["PreferredFlightClass"] = df["PreferredFlightClass"].astype(str)
        df.to_csv("user_profiles.csv", index=False)


def get_user_profile(name):

    df = pd.read_csv("user_profiles.csv")
    user_data = df.loc[df["Name"] == name]
    if not user_data.empty:
        return UserProfile.from_dict(user_data.iloc[0].to_dict())
    return None

def add_user_profile(name):
    new_profile = UserProfile(name)
    df = pd.read_csv("user_profiles.csv")
    df = pd.concat([df, pd.DataFrame([new_profile.to_dict()])], ignore_index=True)
    df.to_csv("user_profiles.csv", index=False)
    return new_profile

def update_user_profile(user_profile):
    filename = "user_profiles.csv"
    try:
        # Ensure the CSV exists
        if not os.path.exists(filename):
            initialise_user_profiles_csv()

        # Load existing profiles
        profiles_df = pd.read_csv(filename)

        # Find the index of the user profile if it exists
        user_index = profiles_df.index[profiles_df["Name"] == user_profile.name].tolist()

        if user_index:
            # Update the existing profile
            profiles_df.loc[user_index[0], "PreferredDateTimeFormat"] = user_profile.preferred_date_time_format
            profiles_df.loc[user_index[0], "PreferredFlightClass"] = user_profile.preferred_flight_class
        else:
            # Add a new profile
            new_profile = {
                "Name": user_profile.name,
                "PreferredDateTimeFormat": user_profile.preferred_date_time_format,
                "PreferredFlightClass": user_profile.preferred_flight_class,
            }
            profiles_df = pd.concat([profiles_df, pd.DataFrame([new_profile])], ignore_index=True)

        # Save updated profiles back to CSV
        profiles_df.to_csv(filename, index=False)
        print(f"Bot: Your profile has been saved successfully, {user_profile.name}.")
    except Exception as e:
        print(f"Bot: An error occurred while saving your profile: {e}")

def get_preferred_format(name):
    user_profile = get_user_profile(name)
    return user_profile.preferred_date_time_format if user_profile else "%Y-%m-%d"

def get_preferred_class(name):
    user_profile = get_user_profile(name)
    return user_profile.preferred_flight_class if user_profile else ""

def update_user_profile(user_profile):
    filename = "user_profiles.csv"
    try:
        # Load existing profiles
        if os.path.exists(filename):
            profiles_df = pd.read_csv(filename)
        else:
            profiles_df = pd.DataFrame(columns=["Name", "PreferredDateTimeFormat", "PreferredFlightClass"])

        # Check if the profile exists
        if user_profile.name in profiles_df["Name"].values:
            profiles_df.loc[profiles_df["Name"] == user_profile.name, ["PreferredDateTimeFormat", "PreferredFlightClass"]] = [
                user_profile.preferred_date_time_format,
                user_profile.preferred_flight_class,
            ]
        else:
            # Append new profile
            new_profile = {
                "Name": user_profile.name,
                "PreferredDateTimeFormat": user_profile.preferred_date_time_format,
                "PreferredFlightClass": user_profile.preferred_flight_class,
            }
            profiles_df = pd.concat([profiles_df, pd.DataFrame([new_profile])], ignore_index=True)

        # Save to CSV
        profiles_df.to_csv(filename, index=False)
        print(f"Bot: Your profile has been saved successfully, {user_profile.name}.")
    except Exception as e:
        print(f"Bot: An error occurred while saving your profile: {e}")

