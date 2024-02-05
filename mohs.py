import pandas as pd

# Read the csv file and save it as a data frame
df = pd.read_csv('Medicare_Physician_Other_Practitioners_by_Provider_and_Service_2021.csv')

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

print(sorted_by_excisions)


min(data['Excisions_per_Mohs'])
max(data['Excisions_per_Mohs'])
plt.hist(data['Excisions_per_Mohs'], bins=range(min()))

import matplotlib.pyplot as plt

# Create a histogram of Excisions_per_Mohs
plt.hist(round(data['Excisions_per_Mohs'], 3), color='lightblue')
plt.axvline(x=mean_value, color='darkblue', linestyle='--')
plt.title('Number of Excisions per Mohs Micrographic Removal of Tumor on Head, Neck, Hands, Feet or Genitalia')
plt.show()
import matplotlib.pyplot as plt

# Create a scatterplot of Excisions_per_Mohs versus Tot_Srvcs
plt.scatter(data['Tot_Srvcs'], data['Excisions_per_Mohs'])
plt.xlabel('Total Services')
plt.ylabel('Excisions per Mohs')
plt.title('Excisions per Mohs Micographic Removal of Tumor vs. Total Services')
plt.show()













# Find the mean, standard deviation, max, and min of the Srvcs_Per_Bene_Day column
mean_value = filtered_data['excisions_per_mohs'].mean()
std_deviation = filtered_data['excisions_per_mohs'].std()
max_value = filtered_data['excisions_per_mohs'].max()
min_value = filtered_data['excisions_per_mohs'].min()
print(f'mean: {mean_value}')
print(f'standard deviation: {std_deviation}')
print(f'max value: {max_value}')
print(f'min value: {min_value}')

import matplotlib.pyplot as plt
plt.scatter(filtered_data['Tot_Srvcs'], excisions_per_mohs)
plt.xlabel('Total Services')
plt.ylabel('Excisions per Mohs')
plt.title('Excisions per Mohs Micographic Removal of Tumor vs. Total Services')
plt.show()

