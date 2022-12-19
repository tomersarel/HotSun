class SolarPanel:
    def __init__(self, amount: int, efficiency: float, lifetime: int, decay_rate: float):
        self.efficiency = efficiency
        self.lifetime = lifetime
        self.decay_rate = decay_rate
        self.amount = amount

    def calc_energy_gen_hourly(self, date):
        # TODO: Calc pv production
        return 2

