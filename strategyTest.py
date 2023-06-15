import numpy as np
import pandas as pd
import datetime
from unittest import TestCase
from hourly_strategy import EconomicGreedyStrategy
from state import State
from battery import Battery
from solar_panel import SolarPanel

class TestEconomicGreedyStrategy(TestCase):
    def test_strategy(self):
        # Create a state with two batteries and two solar panels
        batteries = [Battery(1, datetime.datetime(year=1, day=1, month=1)),Battery(1, datetime.datetime(year=1, day=1, month=1))]
        solar_panels = [SolarPanel(amount=10, max_power=100), SolarPanel(amount=20, max_power=200)]
        state = State(batteries=batteries, solar_panels=solar_panels)

        # Create some sample demand and solar radiation data
        demand = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120,
                           130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240])
        solar_rad = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200])

        # Create an instance of the EconomicGreedyStrategy class
        strategy = EconomicGreedyStrategy()

        # Call the strategy with the state, demand, and solar radiation data
        result, state = strategy(state, demand, solar_rad)

        # Check that the result is a DataFrame with the expected columns
        self.assertIsInstance(result, pd.DataFrame)
        self.assertListEqual(list(result.columns), ['Date', 'Batteries', 'Solar', 'Buying', 'Selling', 'Lost', 'Storaged',
                                                    'NewBatteries', 'AllBatteries', 'AllBatteriesCapacity',
                                                    'AllBatteriesCharge', 'NewSolarPanels', 'AllSolarPanels'])

        # Check that the result has 24 rows
        self.assertEqual(len(result), 24)

        # Check that the batteries and solar panels were not modified
        self.assertListEqual(state.batteries, batteries)
        self.assertListEqual(state.solar_panels, solar_panels)

        # Check that the solar energy production is correct
        self.assertListEqual(list(result['Solar']), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                                     1000, 4000, 9000, 16000, 25000, 36000, 49000, 64000, 81000, 100000, 121000, 144000])

        # Check that the amount of energy bought and sold is correct
        self.assertListEqual(list(result['Buying']), [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120,
                                                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertListEqual(list(result['Selling']), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        # Check that the amount of energy stored in the batteries is correct
        self.assertListEqual(list(result['Storaged']), [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                                        100, 400, 900, 1600, 2500, 3600, 4900, 6400, 8100, 10000, 12100, 14400])

        # Check that the new battery energy and new solar panel power are correct
        self.assertListEqual(list(result['NewBatteries']), [200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200,
                                                            200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200])
        self.assertListEqual(list(result['NewSolarPanels']), [4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000,
                                                              4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000, 4000])



# run the test
if __name__ == '__main__':
    TestEconomicGreedyStrategy().test_strategy()