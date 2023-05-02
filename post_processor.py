import datetime
import logging
import pprint
import unittest
from typing import Dict

# import numpy
import numpy as np
import pandas
import pandas as pd
from tqdm import tqdm
import xmltodict
from collections import OrderedDict

from config_manager import ConfigGetter
from df_objects import HourlyPricesData, HourlyEmmision, HourlySimulationDataOfPeriod


class PostProcessor():
    DATA_TYPES_AMOUNT = 5
    PERIODIC_COST_INDEX = 0
    PERIODIC_PROFIT_INDEX = 1
    PERIODIC_CO2_INDEX = 2
    PERIODIC_SOx_INDEX = 3
    PERIODIC_PMx_INDEX = 4


    def __init__(self, simulation_output: pandas.DataFrame, config):
        time_string_format = config["TIME_FORMAT"]
        self.periods_length_in_days = config["PERIODS_DAYS_AMOUNT"]
        self.start_date = datetime.datetime.strptime(config["START_DATE"], time_string_format)
        end_date = datetime.datetime.strptime(config["END_DATE"], time_string_format)
        self.periods_amount = (end_date - self.start_date).days // self.periods_length_in_days
        self.simulation_output = simulation_output
        logging.info(f"PostProcessor was built successfully.")

    def get_period_dates_by_index(self, period_i: int) -> (datetime.datetime, datetime.datetime):
        period_len = datetime.timedelta(days=self.periods_length_in_days)
        start_date = self.start_date + period_i * period_len + datetime.timedelta(days=1)
        end_date = start_date + period_len  # - datetime.timedelta(hours=1)
        return start_date, end_date

    def run_post_processor(self, set_progress):
        total_benefit = 0
        periodic_data = np.zeros(shape=(self.periods_amount, self.DATA_TYPES_AMOUNT))
        prices = HourlyPricesData()
        emission_rate = HourlyEmmision()
        for period_i in tqdm(range(self.periods_amount), desc="Process Simulation Results...", ):
            logging.info(f"PostProcessor: enters {period_i} period of the post processor.")
            # loads the period data
            start_date, end_date = self.get_period_dates_by_index(period_i)
            simulation_period_output = HourlySimulationDataOfPeriod(self.simulation_output, start_date, end_date)
            # calculates cost, profit and pollution
            periodic_data[period_i][self.PERIODIC_COST_INDEX] = self.calculate_periodic_cost(simulation_period_output,
                                                                                             prices,
                                                                                             start_date,
                                                                                             end_date)
            periodic_data[period_i][self.PERIODIC_PROFIT_INDEX] = self.calculate_periodic_profit(
                simulation_period_output,
                prices,
                start_date,
                end_date)
            total_pollute = self.calculate_periodic_pollute(
                simulation_period_output,
                emission_rate,
                start_date,
                end_date)
            periodic_data[period_i][self.PERIODIC_CO2_INDEX] = total_pollute["CO2"]
            periodic_data[period_i][self.PERIODIC_SOx_INDEX] = total_pollute["SOx"]
            periodic_data[period_i][self.PERIODIC_PMx_INDEX] = total_pollute["PMx"]
            total_benefit += periodic_data[period_i][self.PERIODIC_PROFIT_INDEX] - \
                             periodic_data[period_i][self.PERIODIC_COST_INDEX]

            set_progress((str(period_i + 1), str(self.periods_amount), "Calculate incomes and pollutes...", f"{round((period_i + 1) / self.periods_amount * 100)}%"))

        return pd.DataFrame(periodic_data, columns=['periodic_cost', 'periodic_profit', 'periodic_C02', 'periodic_SOx', 'periodic_PMx']), total_benefit

    def calculate_periodic_cost(self, simulation_period_output: HourlySimulationDataOfPeriod,
                                prices: HourlyPricesData,
                                start_date: datetime.datetime,
                                end_date: datetime.datetime) -> float:
        """
        calculates the cost of the system in a certain period.
        :param simulation_period_output: an object which contains the simulation output of the current period
        :param prices: an object which represents the prices in the period
        :param start_date: the start date of the period
        :param end_date: the end date of the period
        :return: the periodic cost
        """
        # relevant parameters -
        """
        כמות הבטריות * מחיר בטריה
        עלות תחזוק בטריות * כמות הבטריות
        כמות הלוחות הסולרים * מחיר לוח סולרי
        עלות תחזוק לוח סולרי * כמות הלוחות
        כמות החשמל שנקנתה * מחיר החשמל


        מחיר בטריה -> וקטור של capex מcosts-output של nzo
        תחזוק -> אוותו דבר אבל עם opex

        מה חסר לי:
        1) מחירי החשמל
         2) שינוי פורמט של מה אנחנו שומרים מהסימולציה: אני צריכה את כמות הסוללות והלוחות הסולרים שמוסיפים כל שנה
         3) מה זה אומר קנייה לפי ils\kwh?
         4)
        :return:
        """
        buying_prices = prices.get_buying_price_by_range_of_date(start_date, end_date)
        battery_capex_prices = prices.get_battery_capex_by_range_of_date(start_date, end_date)
        panel_capex_prices = prices.get_solar_panel_capex_by_range_of_date(start_date, end_date)
        battery_opex_prices = prices.get_battery_opex_by_range_of_date(start_date, end_date)
        panel_opex_prices = prices.get_solar_panel_opex_by_range_of_date(start_date, end_date)

        cost_of_buying_electricity = np.dot(simulation_period_output.get_electricity_buying(), buying_prices)

        cost_of_batteries = np.dot(simulation_period_output.get_new_batteries(), battery_capex_prices) + \
                            np.dot(simulation_period_output.get_all_batteries(), battery_opex_prices)

        cost_of_panels = np.dot(simulation_period_output.get_new_solar_panels(), panel_capex_prices) + \
                         np.dot(simulation_period_output.get_all_solar_panels(), panel_opex_prices)

        return cost_of_buying_electricity + cost_of_batteries + cost_of_panels

    def calculate_periodic_profit(self, simulation_period_output: HourlySimulationDataOfPeriod,
                                  prices: HourlyPricesData,
                                  start_date: datetime.datetime,
                                  end_date: datetime.datetime) -> float:
        """
        calculates the profit for a given period.
        :param simulation_period_output: an object which contains the simulation output of the current period
        :param prices: an object which represents the price of the electricity each hour, in todo: add units
        :param start_date: the start date of the period
        :param end_date: the end date of the period
        :return: the periodic profit
        """
        period_prices = prices.get_selling_electricity_price_by_range_of_date(start_date, end_date)
        return float(np.dot(simulation_period_output.get_electricity_sells(), period_prices))

    def calculate_periodic_pollute(self, simulation_period_output: HourlySimulationDataOfPeriod,
                                   emission_rate: HourlyEmmision,
                                   start_date: datetime.datetime,
                                   end_date: datetime.datetime) -> Dict[str, float]:
        """
        calculates the profit for a given period.
        :param simulation_period_output: an object which contains the simulation output of the current period
        :param emission_rate: an object which represents the amount of pollute which is caused by the generated bought electricity, in todo: add units
        :param start_date: the start date of the period
        :param end_date: the end date of the period
        :return: the periodic profit
        """
        # TODO: move the constants to a config file
        # the data is presented in units of grams.
        POLLUTION_RATES = {"CO2": 397, "SOx": 0.16, "PMx": 0.02} # units: g/kwh
        periodic_electricity_buying = float(np.sum(simulation_period_output.get_electricity_buying()))
        period_pollution = {"CO2": POLLUTION_RATES["CO2"] * periodic_electricity_buying,
                            "SOx": POLLUTION_RATES["SOx"] * periodic_electricity_buying,
                            "PMx": POLLUTION_RATES["PMx"] * periodic_electricity_buying}  # units: g
        return period_pollution

    def save_output(self, periodic_data: pd.DataFrame) -> None:
        """
        saves the post processor results in a csv file, according to periods
        :param periodic_data: saves the post process data of each period
        :return: None
        """
        periodic_data.to_csv(f'post processor/periodic_data.csv', index=False)
        logging.info(f"Post Processor: the data was saved successfully.")


"""
class PostProcessorTest(unittest.TestCase):
    ConfigGetter.load_data()
    post_processor = PostProcessor()
    total_income = post_processor.run_post_processor()
    post_processor_data = None

    def read_post_processor_data(self):
        titels = ['periodic_cost', 'periodic_profit', 'periodic_pollute']
        df = pd.read_csv("post processor/periodic_data.csv", names=titels)[1:]  # remove the names
        PostProcessorTest.post_processor_data = df.to_numpy()
        pass

    def get_post_processor_data(self, data_type):
        if PostProcessorTest.post_processor_data is None:
            self.read_post_processor_data()
        if data_type == 'periodic_cost':
            return [cost[0] for cost in PostProcessorTest.post_processor_data]
        if data_type == 'periodic_profit':
            return [cost[1] for cost in PostProcessorTest.post_processor_data]
        if data_type == 'periodic_pollute':
            return [cost[1] for cost in PostProcessorTest.post_processor_data]
        pass

    # values for 1 at all the cost parameters, 1 electricity buying per hour, 1 new panel & battery per hour

    def test_periodic_cost(self):
        expected_total_cost = 245280.0
        post_processor_data = self.get_post_processor_data("periodic_cost")
        for period_cost in post_processor_data:
            self.assertEqual(float(expected_total_cost), float(period_cost))
        pass

    def test_periodic_profit(self):
        expected_total_profit = 8760.0
        post_processor_data = self.get_post_processor_data("periodic_profit")
        for period_profit in post_processor_data:
            self.assertEqual(float(expected_total_profit), float(period_profit))
        pass

    def test_periodic_pollution(self):
        expected_total_pollution = 8760.0
        post_processor_data = self.get_post_processor_data("periodic_pollute")
        for period_pollution in post_processor_data:
            self.assertEqual(float(expected_total_pollution), float(period_pollution))
        pass

    def test_total_income(self):
        expected_total_income = (-236520.0) * 33
        self.assertEqual(expected_total_income, PostProcessorTest.total_income)
        pass
"""


def write_electricity_prices_csv_test_values():
    current_date = datetime.datetime(2017, 1, 2, 0, 0, 0)
    end_date = datetime.datetime(2049, 12, 24, 23, 0, 0)
    delta = datetime.timedelta(days=1)
    result = pd.DataFrame(columns=["Date", "Hour", "BuyingElectricityPrice", "SellingElectricityPrice", "BatteryCapex",
                                   "BatteryOpex", "SolarPanelCapex", "SolarPanelOpex"])
    while current_date < end_date:
        day_result = pd.DataFrame(
            {'Date': [(current_date + datetime.timedelta(hours=i)).date().strftime("%d/%m/%Y") for i in range(24)],
             'Hour': [(current_date + datetime.timedelta(hours=i)).time() for i in range(24)],
             'BuyingElectricityPrice': 1, 'SellingElectricityPrice': 1, 'BatteryCapex': 1,
             'BatteryOpex': 1,
             'SolarPanelCapex': [1] * 24, 'SolarPanelOpex': 1})
        result = pd.concat([result, day_result], ignore_index=True)
        current_date += delta

    result.to_csv(f'data/ElectricityPrices.csv', index=False)


def read_raw_electricity_price():
    # Open the file and read the contents
    with open('C:\\Users\\shell\\PycharmProjects\\HotSun\\data\\2022_electricity_prices.xml', 'r',
              encoding='utf-8') as file:
        electricity_raw_prices_xml = file.read()

    # the XML document
    electricity_raw_prices_dicts_list = xmltodict.parse(electricity_raw_prices_xml)['root']['ArrayOfCostExpostsModel'][
        'CostExpostsModel']
    hourly_electricity_prices = {}

    for i in range(0, len(electricity_raw_prices_dicts_list), 2):
        current_datetime = electricity_raw_prices_dicts_list[i]['TimeStamp']
        current_prict = float(electricity_raw_prices_dicts_list[i]['Cost']) + float(
            electricity_raw_prices_dicts_list[i + 1]['Cost'])
        hourly_electricity_prices[current_datetime] = current_prict
    return hourly_electricity_prices


def write_electricity_prices_csv_real_values():
    # data from NZO model
    # todo: find data about 2017-2018-2019, now I have duplicated it from 2020
    pv_yearly_capex = {2017: 3912, 2018: 3912, 2019: 3912, 2020: 3912, 2021: 3784.449, 2022: 3656.898, 2023: 3529.347,
                       2024: 3401.796, 2025: 3274.245, 2026: 3153.275042, 2027: 3032.305084, 2028: 2911.335126,
                       2029: 2790.365168, 2030: 2669.39521, 2031: 2609.061078, 2032: 2548.726946, 2033: 2488.392814,
                       2034: 2428.058683, 2035: 2367.724551, 2036: 2394.855641, 2037: 2421.986731, 2038: 2449.11782,
                       2039: 2476.24891, 2040: 2503.38, 2041: 2465.16, 2042: 2426.94, 2043: 2388.72, 2044: 2350.5,
                       2045: 2312.28, 2046: 2282.952, 2047: 2253.624, 2048: 2224.296, 2049: 2194.968, 2050: 2165.64}

    pv_yearly_opex = {2017: 62.48, 2018: 62.48, 2019: 62.48, 2020: 62.48, 2021: 61.05, 2022: 59.62, 2023: 58.19,
                      2024: 56.76, 2025: 55.33, 2026: 53.50663473, 2027: 51.68326946, 2028: 49.85990419,
                      2029: 48.03653892, 2030: 46.21317365, 2031: 45.2560479, 2032: 44.29892216, 2033: 43.34179641,
                      2034: 42.38467066, 2035: 41.42754491, 2036: 41.21563593, 2037: 41.00372695, 2038: 40.79181796,
                      2039: 40.57990898, 2040: 40.368, 2041: 39.6832, 2042: 38.9984, 2043: 38.3136, 2044: 37.6288,
                      2045: 36.944, 2046: 36.32, 2047: 35.696, 2048: 35.072, 2049: 34.448, 2050: 33.824}

    batteries_yearly_capex = {2017: 1004, 2018: 1004, 2019: 1004, 2020: 1004, 2021: 933.72, 2022: 863.44, 2023: 793.16,
                              2024: 722.88, 2025: 652.6, 2026: 616.456, 2027: 580.312, 2028: 544.168, 2029: 508.024,
                              2030: 471.88, 2031: 451.8, 2032: 431.72, 2033: 411.64, 2034: 391.56, 2035: 371.48,
                              2036: 361.44, 2037: 351.4, 2038: 341.36, 2039: 331.32, 2040: 321.28, 2041: 313.248,
                              2042: 305.216, 2043: 297.184, 2044: 289.152, 2045: 281.12, 2046: 277.104, 2047: 273.088,
                              2048: 269.072, 2049: 265.056, 2050: 261.04}

    batteries_yearly_opex = {2017: 15.6, 2018: 15.6, 2019: 15.6, 2020: 15.6, 2021: 15.04, 2022: 14.48, 2023: 13.92,
                             2024: 13.36, 2025: 12.8, 2026: 12.4, 2027: 12, 2028: 11.6, 2029: 11.2, 2030: 10.8,
                             2031: 10.56, 2032: 10.32, 2033: 10.08, 2034: 9.84, 2035: 9.6, 2036: 9.44, 2037: 9.28,
                             2038: 9.12, 2039: 8.96, 2040: 8.8, 2041: 8.72, 2042: 8.64, 2043: 8.56, 2044: 8.48,
                             2045: 8.4, 2046: 8.32, 2047: 8.24, 2048: 8.16, 2049: 8.08, 2050: 8}

    raw_electricity_price_in_2022 = read_raw_electricity_price()

    current_date = datetime.datetime(2017, 1, 2, 0, 0, 0)
    end_date = datetime.datetime(2049, 12, 24, 23, 0, 0)
    delta = datetime.timedelta(days=1)
    result = pd.DataFrame(columns=["Date", "Hour", "BuyingElectricityPrice", "SellingElectricityPrice", "BatteryCapex",
                                   "BatteryOpex", "SolarPanelCapex", "SolarPanelOpex"])
    while current_date < end_date:
        print(current_date)
        date_array = [current_date.date()] * 24
        hour_array = [(current_date + datetime.timedelta(hours=i)).time() for i in range(24)]
        # calculate the electricity prices. now there is no forcast of growth. todo: add growth forcast
        electricity_prices = []
        for hour, date in enumerate(date_array):
            if date.day == 29 and date.month == 2:
                electricity_prices.append(raw_electricity_price_in_2022[
                                              f'{2022}-{str(date.month).zfill(2)}-{str(date.day - 1).zfill(2)}T{str(hour).zfill(2)}:00:00'])
            elif date.day==25 and date.month==3 and hour == 2:
                electricity_prices.append(raw_electricity_price_in_2022[
                                              f'{2022}-{str(date.month).zfill(2)}-{str(date.day).zfill(2)}T{str(hour-1).zfill(2)}:00:00'])

            else:
                electricity_prices.append(raw_electricity_price_in_2022[
                                              f'{2022}-{str(date.month).zfill(2)}-{str(date.day).zfill(2)}T{str(hour).zfill(2)}:00:00'])

        date_array = [current_date.strftime("%d/%m/%Y") for current_date in date_array]

        day_result = pd.DataFrame(
            {'Date': date_array,
             'Hour': hour_array,
             'BuyingElectricityPrice': electricity_prices,
             'SellingElectricityPrice': electricity_prices,
             'BatteryCapex': batteries_yearly_capex[current_date.year],
             'BatteryOpex': batteries_yearly_opex[current_date.year],
             'SolarPanelCapex': pv_yearly_capex[current_date.year],
             'SolarPanelOpex': pv_yearly_opex[current_date.year]})
        result = pd.concat([result, day_result], ignore_index=True)
        current_date += delta

    result.to_csv(f'data/ElectricityPrices.csv', index=False)


def write_pollution_rates_csv_test_values():
    # was taken from NZO model
    # todo: find 2017-2018-2019 data. now its duplicated from 2020
    yearly_emmition = {2017: 90.62748, 2018: 90.62748, 2019: 90.62748, 2020: 90.62748, 2021: 92.96205613,
                       2022: 95.29663226, 2023: 97.63120839, 2024: 99.96578452, 2025: 102.3003606, 2026: 104.9540253,
                       2027: 107.60769, 2028: 110.2613546, 2029: 112.9150193, 2030: 115.5686839, 2031: 118.3146748,
                       2032: 121.0606657, 2033: 123.8066566, 2034: 126.5526474, 2035: 129.2986383, 2036: 132.3933617,
                       2037: 135.488085, 2038: 138.5828083, 2039: 141.6775317, 2040: 144.772255, 2041: 147.9463361,
                       2042: 151.1204173, 2043: 154.2944984, 2044: 157.4685796, 2045: 160.6426607, 2046: 164.2097231,
                       2047: 167.7767855, 2048: 171.3438479, 2049: 174.9109102, 2050: 178.4779726}
    current_date = datetime.datetime(2017, 1, 2, 0, 0, 0)
    end_date = datetime.datetime(2049, 12, 24, 23, 0, 0)
    delta = datetime.timedelta(days=1)
    result = pd.DataFrame(columns=["Date", "Hour", "Pollution"])
    while current_date < end_date:
        day_result = pd.DataFrame(
            {'Date': [(current_date + datetime.timedelta(hours=i)).date().strftime("%d/%m/%Y") for i in range(24)],
             'Hour': [(current_date + datetime.timedelta(hours=i)).time() for i in range(24)],
             'Pollution': yearly_emmition[current_date.year]})
        result = pd.concat([result, day_result], ignore_index=True)
        current_date += delta

    result.to_csv(f'data/PollutionRates.csv', index=False)


if __name__ == '__main__':
    # unittest.main()
    # write_electricity_prices_csv()
    # write_pollution_rates_csv()
    #write_pollution_rates_csv_test_values()
    pass
