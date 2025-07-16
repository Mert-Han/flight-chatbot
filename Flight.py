class Flight:
    def __init__(self, date=None, origin=None, destination=None, flight_class=None):
        self.date = date
        self.origin = origin
        self.destination = destination
        self.flight_class = flight_class

    def set_date(self, date):
        self.date = date

    def get_date(self):
        return self.date

    def set_origin(self, origin):
        self.origin = origin

    def get_origin(self):
        return self.origin

    def set_destination(self, destination):
        self.destination = destination

    def get_destination(self):
        return self.destination

    def set_flight_class(self, flight_class):
        self.flight_class = flight_class

    def get_flight_class(self):
        return self.flight_class

    def __repr__(self):
        return f"Flight(date={self.date}, origin={self.origin}, destination={self.destination}, flight_class={self.flight_class})"
