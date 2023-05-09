
from demands_cal import *

import unittest


class TestFunctions(unittest.TestCase):
    def test_hotels_average_monthly_demand_2021(self):
        # Set the arguments for the hotels_demand_table function
        amount = 1000
        amount_growth = 1.01
        demand_growth = 1.02
        demand = 5000

        # Call the total_demand_table function with the specified arguments
        result = hotels_demands_table(amount,amount_growth,demand_growth,demand)

        # Calculate the average monthly demand for the year 2021 from the result of the total_demand_table function
        monthly_demands = [sum([sum(day) for day in month]) for month in result[2021]]
        average_monthly_demand = sum(monthly_demands) / len(monthly_demands)

        # Check if the calculated average monthly demand is almost equal to the expected value
        self.assertTrue(self,math.isclose(average_monthly_demand/(demand*amount),1,abs_tol=0.001))

    def test_business_average_monthly_demand_2021(self):
        # Set the arguments for the hotels_demand_table function
        amount = 1000
        amount_growth = 1.01
        demand_growth = 1.02
        demand = 5000

        # Call the total_demand_table function with the specified arguments
        result = businesses_demands_table(amount,amount_growth,demand_growth,demand)

        # Calculate the average monthly demand for the year 2021 from the result of the total_demand_table function
        monthly_demands = [sum([sum(day) for day in month]) for month in result[2021]]
        average_monthly_demand = sum(monthly_demands) / len(monthly_demands)

        # Check if the calculated average monthly demand is almost equal to the expected value
        self.assertTrue(self,math.isclose(average_monthly_demand/(demand*amount),1,abs_tol=0.001))

    def test_industry_average_monthly_demand_2021(self):
        # Set the arguments for the hotels_demand_table function
        amount = 1000
        amount_growth = 1.01
        demand_growth = 1.02
        demand = 5000

        # Call the total_demand_table function with the specified arguments
        result = industry_demands_table(amount,amount_growth,demand_growth,demand)

        # Calculate the average monthly demand for the year 2021 from the result of the total_demand_table function
        monthly_demands = [sum([sum(day) for day in month]) for month in result[2021]]
        average_monthly_demand = sum(monthly_demands) / len(monthly_demands)

        # Check if the calculated average monthly demand is almost equal to the expected value
        self.assertTrue(self,math.isclose(average_monthly_demand/(demand*amount),1,abs_tol=0.001))

    def test_factories_average_monthly_demand_2021(self):
        # Set the arguments for the hotels_demand_table function
        amount = 1000
        amount_growth = 1.01
        demand_growth = 1.02
        demand = 5000

        # Call the total_demand_table function with the specified arguments
        result = factories_demands_table(amount,amount_growth,demand_growth,demand)

        # Calculate the average monthly demand for the year 2021 from the result of the total_demand_table function
        monthly_demands = [sum([sum(day) for day in month]) for month in result[2021]]
        average_monthly_demand = sum(monthly_demands) / len(monthly_demands)

        # Check if the calculated average monthly demand is almost equal to the expected value
        self.assertTrue(self,math.isclose(average_monthly_demand/(demand*amount),1,abs_tol=0.001))


    def test_average_monthly_demand_2021(self):
        # Set the arguments for the total_demand_table function
        population_at_2021 = 1000
        population_growth = 1.01
        average_wage = 30000
        people_per_household = 4
        workers_per_household = 2
        hotels_amount = 1000
        hotels_amount_growth = 1.01
        hotels_demand_growth = 1.02
        hotels_demand = 5000
        businesses_amount = 1000
        businesses_amount_growth = 1.01
        businesses_demand_growth = 1.02
        businesses_demand = 5000
        factories_amount = 1000
        factories_amount_growth = 1.01
        factories_demand_growth = 1.034
        factories_demand = 5000
        industry_amount = 1000
        industry_amount_growth = 1.01
        industry_demand_growth = 1.034
        industry_demand = 5000

        # Call the total_demand_table function with the specified arguments
        result = total_demand_table(population_at_2021, population_growth, average_wage, people_per_household,
                                    workers_per_household,
                                    hotels_amount, hotels_amount_growth, hotels_demand_growth, hotels_demand,
                                    businesses_amount, businesses_amount_growth, businesses_demand_growth,
                                    businesses_demand,
                                    factories_amount, factories_amount_growth, factories_demand_growth,
                                    factories_demand,
                                    industry_amount, industry_amount_growth, industry_demand_growth, industry_demand)

        # Calculate the average monthly demand for the year 2021 from the result of the total_demand_table function
        monthly_demands = [
            sum([sum(day) for day in result[2021][i]]) - houses_demand(population_at_2021, population_growth,
                                                                       average_wage, people_per_household,
                                                                       workers_per_household, (2021, i))
            for i in range(12)]
        average_monthly_demand = sum(monthly_demands) / len(monthly_demands)

        # Check if the calculated average monthly demand is almost equal to the expected value
        self.assertTrue(self, math.isclose(average_monthly_demand / (
                    hotels_demand * hotels_amount + businesses_demand * businesses_amount + factories_demand * factories_amount + industry_demand * industry_amount),
                                           1, abs_tol=0.001))

if __name__ == '__main__':
    unittest.main()