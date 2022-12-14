import datetime
import pandas as pd
import numpy as np


class DemandHourly:
    """
    This class wraps the predicted consumption db
    """
    def __init__(self):
        titles = ["Date", "PartOfTheDay", 1, 2, 3,4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.df = pd.read_csv("data/hourlyConsumptionPrediction.csv", names=titles)
        self.df['Date'] = pd.to_datetime(self.df['Date'], dayfirst=True)

    def get_demand_daily_by_date(self, date: datetime.datetime):
        """
        return the predicted consumption in given date
        :param date: the requested time
        :return: arr of the power consumption at that day by hour
        """
        return self.get_demand_daily_by_range_of_date(date, date + datetime.timedelta(days=1))

    def get_demand_daily_by_range_of_date(self, start_date: datetime.datetime, end_date: datetime.datetime):
        """
        return the predicted consumption in given range of date (including start_date excluding end_date)
        :param end_date: the start date
        :param start_date: the end date
        :return: arr of the power consumption at that date range by hour
        """
        # TODO: normalize the data that wil fit the city

        # make sure the dates are at the beginning of the day
        start_date = start_date.replace(hour=0)
        end_date = end_date.replace(hour=0)

        period = self.df[(self.df['Date'] >= start_date) & (self.df['Date'] < end_date)].to_numpy()
        hourly_consumption_arr = np.concatenate([day[2:] for day in period])  # remove PartOfTheDay and the date
        return hourly_consumption_arr


class PVProduction:
    def __init__(self):
        pass

    def get_production_by_date(self, date: datetime.datetime):
        pass


