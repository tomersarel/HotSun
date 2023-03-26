#date=(year,month)
import math
income_quintile_payments = {
    0:0.66810,
    11000: 0.80048,
    16000: 0.95702,
    23000: 1.12801,
    32000: 1.44691
}
demands_growth = 1.04
demand_for_month_in_2021 = {
    0:1904,
    1:1574,
    2:1598,
    3:1292,
    4:1375,
    5:1625,
    6:2307,
    7:2436,
    8:1995,
    9:1430,
    10:1206,
    11:1744
}
def houses_demand(population, population_growth, average_wage, people_per_household,workers_per_household, date):
    updated_population = population * math.pow(population_growth,date[0]-2021)
    households = updated_population/people_per_household
    income_factor = income_quintile_payments[max([i for i in income_quintile_payments.keys() if i<workers_per_household*average_wage])]
    total_demand= math.pow(demands_growth,date[0]-2021)*households*income_factor*demand_for_month_in_2021[date[1]]
    return total_demand
hotel_demand_for_month_factor = {}
def hotel_demand(amount,amount_growth,demand_growth,demand,date):
    return amount*math.pow(amount_growth,date[0]-2021)*hotel_demand_for_month_factor[date[1]]\
           *math.pow(demand_growth,date[0]-2021)*demand
def businesses_demand(amount,amount_growth,demand_growth,demand,date):
    return amount * math.pow(amount_growth, date[0] - 2021) \
           * math.pow(demand_growth, date[0] - 2021) * demand
def factories_demand(amount,amount_growth,demand_growth,demand,date):
    return amount * math.pow(amount_growth, date[0] - 2021) \
           * math.pow(demand_growth, date[0] - 2021) * demand