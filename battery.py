import datetime
import unittest
import json
import logging


class Battery:
    THRESHOLD = 10 ** -10
    CONFIG_SIM = "config_sim.json"

    def __init__(self, amount: int, date: datetime.datetime, config_name=CONFIG_SIM):
        logging.basicConfig(filename="battery_logger.log", level=logging.DEBUG)
        try:
            with open(config_name) as config_file:
                config = config_file.read()
        except IOError as e:
            logging.critical(f" Couldn't open config file {config_name}")
            raise e

        try:
            config_battery = json.loads(config)['battery']
            self.capacity = config_battery['capacity'] * amount
            self.lifetime = config_battery['lifetime']
            self.current_energy = 0
            self.efficiency = config_battery['efficiency']
            self.charge_rate = config_battery['charge_rate']
            self.date = date
            self.decay_rate = config_battery['decay_rate']
        except KeyError as e:
            logging.error(" Couldn't find battery configuration")
            # TODO: Use default arguments
            raise e

    def update_efficiency(self, current_date: datetime.datetime):
        # TODO: Change to generic period
        self.efficiency -= (current_date - self.date) / datetime.timedelta(days=365) * self.decay_rate
        self.date = current_date

    def get_max_charge(self):
        """
        Max possible charge to be charged at e given state
        :return:
        """
        max_charge = (self.capacity - self.current_energy)
        # The theoretical upper bound is the total capacity multiplied by charge rate
        return min(max_charge, self.charge_rate) / self.efficiency

    def try_charge(self, energy_kwh):
        """
        Tries to load the battery with the given energy
        Charge as mush energy as possible from the given energy and returns it
        :param energy_kwh:
        :return:
        """
        if self.current_energy == self.capacity:
            return 0
        allowed_charge = min(self.get_max_charge(), energy_kwh)
        self.current_energy += self.efficiency * allowed_charge
        logging.info(f" Charged {allowed_charge} to battery {self}")
        return allowed_charge * self.efficiency

    def get_max_discharge(self):
        return min([self.current_energy, self.charge_rate]) * self.efficiency

    def try_discharge(self, energy_kwh):
        if self.current_energy == 0:
            return 0
        # In order to get energy E, we have to discharge E / self.efficiency
        allowed_discharge = min(self.get_max_discharge(), energy_kwh)
        self.current_energy -= allowed_discharge / self.efficiency
        logging.info(f" Discharged {allowed_discharge} from battery {self}")

        if self.current_energy < self.THRESHOLD:
            self.current_energy = 0

        return allowed_discharge

    def get_energy_kwh(self):
        return self.current_energy

    def get_capacity_kwh(self):
        return self.capacity

    def __str__(self):
        return f"capacity: {self.capacity}, lifetime:{self.lifetime}," \
               f"charge_rate: {self.charge_rate}, efficiency: {self.efficiency}," \
               f"current_energy: {self.current_energy}, decay_rate: {self.decay_rate}," \
               f"date:{self.date}"

    def __repr__(self):
        return str(self)


class BatteryTest(unittest.TestCase):
    def test_basic_full_efficiency(self):
        battery = Battery(1, datetime.datetime(year=1, day=1, month=1), config_name='test_full_efficiency.json')
        self.assertEqual(battery.get_capacity_kwh(), 200)
        self.assertEqual(battery.get_energy_kwh(), 0)
        self.assertEqual(battery.get_max_charge(), 70)
        self.assertEqual(battery.get_max_discharge(), 0)

        self.assertEqual(battery.try_charge(100), 70)
        self.assertEqual(battery.get_energy_kwh(), 70)
        self.assertEqual(battery.get_max_discharge(), 70)

        self.assertEqual(battery.try_discharge(40), 40)
        self.assertEqual(battery.get_energy_kwh(), 30)
        self.assertEqual(battery.get_max_discharge(), 30)

        self.assertEqual(battery.try_discharge(50), 30)
        self.assertEqual(battery.get_energy_kwh(), 0)
        self.assertEqual(battery.get_max_discharge(), 0)

        self.assertEqual(battery.get_capacity_kwh(), 200)

    def test_efficiency(self):
        efficiency = 0.9
        battery = Battery(1, datetime.datetime(year=1, day=1, month=1), config_name='config_sim.json')
        self.assertEqual(battery.get_capacity_kwh(), 200)
        self.assertEqual(battery.get_energy_kwh(), 0)
        self.assertEqual(battery.get_max_charge(), 70 / efficiency)
        self.assertEqual(battery.get_max_discharge(), 0)

        self.assertEqual(battery.try_charge(100), 70)
        self.assertEqual(battery.get_energy_kwh(), 70)
        self.assertEqual(battery.get_max_discharge(), 70 * efficiency)

        self.assertEqual(battery.try_discharge(40), 40)
        self.assertEqual(battery.get_energy_kwh(), 70-40/efficiency)
        self.assertEqual(battery.get_max_discharge(), (70 - 40/efficiency)*efficiency)

        self.assertEqual(battery.try_discharge(50), (70-40/efficiency)*efficiency)
        self.assertEqual(battery.get_energy_kwh(), 0)
        self.assertEqual(battery.get_max_discharge(), 0)

        self.assertEqual(battery.get_capacity_kwh(), 200)

    def test_efficiency_changes(self):
        efficiency1 = 0.9
        decay_rate = 0.2
        efficiency2 = efficiency1 - decay_rate

        battery = Battery(1, datetime.datetime(year=1, day=1, month=1), config_name='config_sim.json')
        self.assertEqual(battery.get_capacity_kwh(), 200)
        self.assertEqual(battery.get_energy_kwh(), 0)
        self.assertEqual(battery.get_max_charge(), 70 / efficiency1)
        self.assertEqual(battery.get_max_discharge(), 0)

        self.assertEqual(battery.try_charge(100), 70)
        self.assertEqual(battery.get_energy_kwh(), 70)
        self.assertEqual(battery.get_max_discharge(), 70 * efficiency1)
        battery.update_efficiency(datetime.datetime(year=2, day=1, month=1))

        self.assertEqual(battery.try_discharge(40), 40)
        self.assertEqual(battery.get_energy_kwh(), 70 - 40 / efficiency2)
        self.assertEqual(battery.get_max_discharge(), (70 - 40 / efficiency2) * efficiency2)

        self.assertEqual(battery.try_discharge(50), (70 - 40 / efficiency2) * efficiency2)
        self.assertEqual(battery.get_energy_kwh(), 0)
        self.assertEqual(battery.get_max_discharge(), 0)

        self.assertEqual(battery.get_capacity_kwh(), 200)


if __name__ == '__main__':
    unittest.main()
