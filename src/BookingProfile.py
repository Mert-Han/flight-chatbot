from Flight import Flight

class BookingProfile:
    def __init__(self):
        self.user_name = None
        self.departure_flight = None  # Flight object for departure
        self.return_flight = None    # Flight object for return (if applicable)
        self.return_status = False  # Default to one-way

    # Personalisation
    def set_name(self, name):
        self.user_name = name

    def get_name(self):
        return self.user_name

    # Getters and setters for departure flight
    def set_origin(self, origin):
        if not self.departure_flight:
            self.departure_flight = Flight(origin=origin)
        else:
            self.departure_flight.set_origin(origin)

    def get_origin(self):
        return self.departure_flight.get_origin() if self.departure_flight else None

    def set_destination(self, destination):
        if not self.departure_flight:
            self.departure_flight = Flight(destination=destination)
        else:
            self.departure_flight.set_destination(destination)

    def get_destination(self):
        return self.departure_flight.get_destination() if self.departure_flight else None

    def set_departure_date(self, departure_date):
        if not self.departure_flight:
            self.departure_flight = Flight(date=departure_date)
        else:
            self.departure_flight.set_date(departure_date)

    def get_departure_date(self):
        return self.departure_flight.get_date() if self.departure_flight else None

    # Getters and setters for return flight
    def set_return_date(self, return_date=None):
        if not self.return_flight:
            self.return_flight = Flight(date=return_date)
        else:
            self.return_flight.set_date(return_date)

    def get_return_date(self):
        return self.return_flight.get_date() if self.return_flight else None

    def set_return_status(self, return_status):
        self.return_status = return_status
        if return_status and not self.return_flight:
            self.return_flight = Flight()  # Create an empty Flight object for return flight

    def get_return_status(self):
        return self.return_status

    # Utility methods for flights
    def set_departure_flight_class(self, flight_class):
        if not self.departure_flight:
            self.departure_flight = Flight(flight_class=flight_class)
        else:
            self.departure_flight.set_flight_class(flight_class)

    def get_departure_flight_class(self):
        return self.departure_flight.get_flight_class() if self.departure_flight else None

    def set_return_flight_class(self, flight_class):
        if not self.return_flight:
            self.return_flight = Flight(flight_class=flight_class)
        else:
            self.return_flight.set_flight_class(flight_class)

    def get_return_flight_class(self):
        return self.return_flight.get_flight_class() if self.return_flight else None
