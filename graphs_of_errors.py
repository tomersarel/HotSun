import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

'''maxi = pd.read_csv('maximum_capacity.csv')
mini = pd.read_csv('minimum_capacity.csv')
plt.plot([i for i in maxi.index], maxi['Batteries'] - mini['Batteries'])
plt.ylabel('some numbers')

maxi = pd.read_csv('maximum_charge_rate.csv')
mini = pd.read_csv('minimum_charge_rate.csv')
plt.plot([i for i in maxi.index], maxi['Batteries'] - mini['Batteries'])
plt.ylabel('some numbers')

maxi = pd.read_csv('maximum_decay_rate.csv')
mini = pd.read_csv('minimum_decay_rate.csv')
plt.plot([i for i in maxi.index], maxi['Batteries'] - mini['Batteries'])
plt.ylabel('some numbers')

maxi = pd.read_csv('maximum_efficiency.csv')
mini = pd.read_csv('minimum_efficiency.csv')
plt.plot([i for i in maxi.index], maxi['Batteries'] - mini['Batteries'])
plt.ylabel('some numbers')

maxi = pd.read_csv('maximum_lifetime.csv')
mini = pd.read_csv('minimum_lifetime.csv')
plt.plot([i for i in maxi.index], maxi['Batteries'] - mini['Batteries'])
plt.ylabel('some numbers')
'''

data = pd.read_csv('totalprecent_capacity.csv')
lst = [i for i in data.index]
plt.plot([i for i in data.index], data['1'],)
plt.ylabel('some numbers')
plt.show()
# [0:289079]
