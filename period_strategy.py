class PeriodStrategy:
    def __init__(self, solar_panels_kW: float, batteries_kWh: float, config: dict):
        self.solar_panels = solar_panels_kW / config['solar']['peakpower']
        self.batteries = batteries_kWh
        