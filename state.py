import datetime
from battery import Battery
from solar_panel import SolarPanel


class State:
    def __init__(self, start_date: datetime.datetime):
        self.batteries = []
        self.solar_panels = []
        self.current_date = start_date
        self.occupied_area = 0

