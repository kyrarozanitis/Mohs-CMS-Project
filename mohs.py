import pandas as pd
import textwrap
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import geopandas as gpd

# Read the csv file and save it as a data frame
df = pd.read_csv('Medicare_Physician_Other_Practitioners_by_Provider_and_Service_2021.csv')
physicians = pd.read_csv('Medicare_Physician_Other_Practitioners_by_Provider_2021.csv')

# Get the names of the columns in the data frame
column_names = df.columns.tolist()

# Print the column names
print(column_names)  
# Display the first 10 rows of the data frame
print(df.head(10))
# Filter the data for all rows where HCPCS_Cd equals 17311 and 17312
filtered_data = df[df['HCPCS_Cd'].isin([17311, 17312])]
data_17311 = df[df['HCPCS_Cd'].isin([17311])]

doctors_to_remove = filtered_data.loc[(filtered_data['HCPCS_Cd'] == 17311) & (filtered_data['Tot_Srvcs'] < 20), 'Rndrng_NPI'].tolist()
filtered_data = filtered_data[~filtered_data['Rndrng_NPI'].isin(doctors_to_remove)]
filtered_data['Rndrng_NPI'].nunique()

# This groups filtered data into a bunch of small tables, one per doctor with two rows. Then takes the sum of Tot_Srvcs for both 17311 and 17312 and creates a table with Rndrng_NPI and tot_srvcs
data = filtered_data.groupby('Rndrng_NPI').agg({'Tot_Srvcs': 'sum'}).reset_index()
# This renames Tot_Srvcs to Tot_rounds because if you add 17311 and 17322 procedures it is the total number of rounds done
data['Tot_Rounds'] = data['Tot_Srvcs']
newdata = data_17311.groupby('Rndrng_NPI').agg({'Tot_Srvcs': 'sum'}).reset_index()
# This line uses the table data_17311 and adds the total number of 17311 procedures done by each doctor to the table
data['Tot_Srvcs'] = data.apply(lambda row: newdata.loc[newdata['Rndrng_NPI'] == row['Rndrng_NPI'], 'Tot_Srvcs'].values[0] if row['Rndrng_NPI'] in newdata['Rndrng_NPI'].values else row['Tot_Srvcs'], axis=1)
# This calculates excisions per mohs
data['Excisions_per_Mohs'] = data['Tot_Rounds']/data['Tot_Srvcs']

sorted_by_excisions= data.sort_values(by='Tot_Srvcs', ascending=False).head()
correlation = data['Tot_Srvcs'].corr(data['Excisions_per_Mohs']) 
print("Correlation between Tot_Srvcs and Excisions_per_Mohs:", correlation)


print(sorted_by_excisions)

excisions_per_mohs = data['Excisions_per_Mohs']
lower_bound = np.percentile(excisions_per_mohs, 0)
upper_bound = np.percentile(excisions_per_mohs, 90)
range_95 = (lower_bound, upper_bound)
print("Range of the middle 95% of values in Excisions_per_Mohs:", range_95)

# Create a histogram of Excisions_per_Mohs
mean_value = data['Excisions_per_Mohs'].mean()
plt.title('\n'.join(textwrap.wrap('Figure 1. U.S. Physicians Excisions per MOHS procedure in 2021', 40)), fontweight='bold', fontsize=16)
plt.hist(data['Excisions_per_Mohs'], bins=30, range=(1, 4), color='lightblue', edgecolor='black')
plt.axvline(mean_value, color='red', linestyle='dashed', label=f'Mean: {mean_value:.2f}')
plt.legend()
plt.show()

mohs_physicians = pd.merge(data, physicians, on='Rndrng_NPI', how='inner')
state_average = mohs_physicians.groupby('Rndrng_Prvdr_State_Abrvtn')['Excisions_per_Mohs'].mean().reset_index()
state_count = mohs_physicians['Rndrng_Prvdr_State_Abrvtn'].value_counts().reset_index()
state_count.columns = ['Rndrng_Prvdr_State_Abrvtn', 'state_count']

# Load US states shapefile
us_states = gpd.read_file("shapefiles\cb_2018_us_state_500k.shp")

# Merge data with the shapefile
us_states = us_states.merge(state_average, how='left', left_on='STUSPS', right_on='Rndrng_Prvdr_State_Abrvtn')

# Create main plot for continental US
fig, ax = plt.subplots(1, 1, figsize=(20, 10))
us_states[~us_states['STUSPS'].isin(['HI', 'AK', 'PR', 'VI', 'GU', 'MP', 'AS'])].plot(column='Excisions_per_Mohs', cmap='YlGnBu', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
ax.set_title('Figure 2. Average Excisions per Mohs Procedure by State in 2021', fontsize=16, fontweight='bold')

# Create inset for Alaska
ax_ak = fig.add_axes([0.0, -0.25, 1, 1])  # position and size of the inset (left, bottom, width, height)
us_states[us_states['STUSPS'] == 'AK'].plot(column='Excisions_per_Mohs', cmap='YlGnBu', linewidth=0.8, ax=ax_ak, edgecolor='0.8')

# Create inset for Hawaii
ax_hi = fig.add_axes([-0.15, 0.1, 0.5, 0.5])  # position and size of the inset (left, bottom, width, height)
us_states[us_states['STUSPS'] == 'HI'].plot(column='Excisions_per_Mohs', cmap='YlGnBu', linewidth=0.8, ax=ax_hi, edgecolor='0.8')

ax.axis('off')
ax_ak.axis('off')
ax_hi.axis('off')

plt.show()

'''
# Create a scatterplot of Excisions_per_Mohs versus Tot_Srvcs
filtered_data = data[data['Tot_Srvcs'] < 3000]
plt.scatter(filtered_data['Tot_Srvcs'], filtered_data['Excisions_per_Mohs'])
plt.xlabel('Total Services')
plt.ylabel('Excisions per Mohs')
plt.title('Excisions per Mohs Micographic Removal of Tumor vs. Total Services')
plt.show()
'''
