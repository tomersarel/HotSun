import datetime


class Battery:
    def __init__(self, amount: int, capacity: float, lifetime: int, charge_rate: float, date: datetime.date, efficiency=100):
        self.capacity = capacity
        self.lifetime = lifetime
        self.current_energy = 0
        self.efficiency = efficiency
        self.charge_rate = charge_rate
        self.date = date  # consider delete
        self.amount = amount
