class UserProfile:
    """
    Represents a user's profile, including their name,
    preferred date-time format, and flight class.
    """

    def __init__(self, name, preferred_date_time_format="%A, %d %B %Y", preferred_flight_class=""):

        self.name = name
        self.preferred_date_time_format = preferred_date_time_format
        self.preferred_flight_class = preferred_flight_class

    def to_dict(self):
  
        return {
            "Name": self.name,
            "PreferredDateTimeFormat": self.preferred_date_time_format,
            "PreferredFlightClass": self.preferred_flight_class
        }

    @staticmethod
    def from_dict(data):
        return UserProfile(
            name=data.get("Name", ""),
            preferred_date_time_format=data.get("PreferredDateTimeFormat", "%Y-%m-%d"),
            preferred_flight_class=data.get("PreferredFlightClass", "")
        )

    def __str__(self):
        return (
            f"UserProfile(Name: {self.name}, "
            f"PreferredDateTimeFormat: {self.preferred_date_time_format}, "
            f"PreferredFlightClass: {self.preferred_flight_class})"
        )
