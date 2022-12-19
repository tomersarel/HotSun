import df_objects
import state
from abc import ABC


class DailyStrategy(ABC):
    def __call__(self, demand: df_objects.DemandHourly, state: state.State):
        pass


class GreedyDailyStrategy(DailyStrategy):
    def __call__(self, demand: df_objects.DemandHourly, state: state.State):
        simulation_result = [{"solar": 0, "storage": 0, "external_network": 0, "selling": 0}]