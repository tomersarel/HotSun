import datetime


class State:
    def __init__(self, period_time: float, start_date: datetime.datetime, end_date: datetime.datetime):
        self.batteries = [None] * int((end_date - start_date) / datetime.timedelta(days=365.2425 * period_time))
        self.solar_panels = [None] * int((end_date - start_date) / datetime.timedelta(days=365.2425 * period_time))
        self.date = start_date
        self.occupied_area = 0
