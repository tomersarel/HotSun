class SolarPanel:
    def __init__(self, amount: int, efficiency: float, lifetime: int, degradation_rate: float):
        self.efficiency = efficiency
        self.lifetime = lifetime
        self.degradation_rate = degradation_rate
        self.amount = amount

    def calc_energy_gen_hourly(self, date):
        pass

