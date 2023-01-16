from abc import ABC
from datetime import datetime, timedelta
from config_manager import ConfigGetter


class ProcessManager(ABC):
    """
    a class which represents a generic process manager, which scans the whole period.
    """

    def __init__(self):
        # giving default values to the data which will be read from the json
        self.periods_length_in_days = 0
        self.start_date = datetime.now()
        self.periods_amount = 0
        self.read_json_data()

    def read_json_data(self):
        time_string_format = ConfigGetter["TIME_FORMAT"]
        self.periods_length_in_days = ConfigGetter["PERIODS_DAYS_AMOUNT"]
        # reads the start & end date as a datetime object
        self.start_date = datetime.strptime(ConfigGetter["START_DATE"], time_string_format)
        end_date = datetime.strptime(ConfigGetter["END_DATE"], time_string_format)
        self.periods_amount = (end_date - self.start_date).days // self.periods_length_in_days

    def convert_period_index_to_dates(self, period_i: int) -> (datetime, datetime):
        """
        convert period index to the start date of the period and the end date of the period.
        :param period_i: the index of the period
        :return: the start date of the period and the end date of the period.
        """
        period_start_date = self.start_date + timedelta(days=self.periods_length_in_days) * period_i
        period_end_date = self.start_date + timedelta(days=self.periods_length_in_days) * (period_i + 1)
        return period_start_date, period_end_date
