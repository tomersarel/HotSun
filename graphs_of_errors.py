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
orig = pd.read_csv('original_data')

def calculate_percent(maxi, mini):
    # converting the normal pandas to numpy
    np_orig = orig.to_numpy()
    # taking the inverse for each box != 0
    reciprocal_values = np.reciprocal(np_orig, where=np_orig != 0)
    # return to pandas
    pd_df_with_nones = pd.DataFrame(reciprocal_values)
    # replace nan with 0
    pd_df_with_nones.fillna(0, inplace=True)
    # back to numpy
    reciprocal_values = pd_df_with_nones.to_numpy()

    upercent = (maxi - orig) * reciprocal_values * 100
    downpercent = (orig - mini) * reciprocal_values * 100
    totpercent = upercent + downpercent

    total_percent = pd.DataFrame(totpercent)
    up_percent = pd.DataFrame(upercent)
    down_percent = pd.DataFrame(downpercent)

    # frames = [total_percent, up_percent, down_percent]

    # final_percent = pd.concat(frames)

    return total_percent


np_orig = orig.to_numpy()
# taking the inverse for each box != 0
reciprocal_values = np.reciprocal(np_orig, where=np_orig != 0)
# return to pandas
pd_df_with_nones = pd.DataFrame(reciprocal_values)
# replace nan with 0
pd_df_with_nones.fillna(0, inplace=True)
# back to numpy
inverse = pd_df_with_nones.to_numpy()



maximum = pd.read_csv('maximum_capacity.csv')
minimum = pd.read_csv('minimum_capacity.csv')
data = calculate_percent(maximum, minimum)
plt.plot(data['Solar'])
plt.ylabel('some numbers')
plt.show()
# [0:289079]
