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

    def get_demand_daily__by_date(self, date: datetime.datetime):
        """
        return the predicted consumption in given date
        :param date: the requested time
        :return: arr of the power consumption at that day
        """
        # TODO: normalize the data that wil fit the city
        daily = self.df[(self.df['Date'] == date.strftime("%d/%m/20%y"))].to_numpy()

        return np.append(daily[0][2:], daily[1][2:])


class PVProduction:
    def __init__(self):
        pass

    def get_production_by_date(self, date: datetime.datetime):
        pass


