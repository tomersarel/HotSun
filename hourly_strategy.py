import df_objects
from df_objects import *
from state import State


def generic_hourly_strategy(state: State, demand: df_objects.DemandHourly, solar_rad: df_objects.SolarRadiationHourly):

    result = pd.DataFrame({'Date': [state.current_date + datetime.timedelta(hours=i) for i in range(24)],
                           'Batteries': [1] * 24, 'Solar': [1] * 24, 'Buying': [1] * 24, 'Selling': [1] * 24,
                           'Lost': [1] * 24})
    state.current_date += datetime.timedelta(days=1)
    return result, state
