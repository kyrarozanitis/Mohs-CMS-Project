# import necessary libraries
import pandas as pd
import textwrap
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import os
import os
import pandas as pd

def calculate_excisions_per_mohs():
    """
    Calculate the excisions per Mohs for a given dataset.

    This function reads a CSV file containing Medicare physician data, filters the data for specific HCPCS codes,
    removes doctors with less than 20 total services for a specific HCPCS code, groups the data by doctor,
    calculates the excisions per Mohs, and prints the results.

    Returns:
    None
    """
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

    # Sort data_17311 by Tot_Srvcs in ascending order
    sorted_data_17311 = data_17311.sort_values('Tot_Srvcs')

    # Print the sorted data
    print(sorted_data_17311)

    # Find and remove doctors with less than 20 total services for 17311
    doctors_to_remove = filtered_data.loc[(filtered_data['HCPCS_Cd'] == 17311) & (filtered_data['Tot_Srvcs'] < 20), 'Rndrng_NPI'].tolist()
    print("Number of doctors included in doctors_to_remove:", len(doctors_to_remove))
    filtered_data = filtered_data[~filtered_data['Rndrng_NPI'].isin(doctors_to_remove)]
    filtered_data['Rndrng_NPI'].nunique()

    # Group filtered data into a bunch of small tables, one per doctor with two rows.
    # Then take the sum of Tot_Srvcs for both 17311 and 17312 and create a table with Rndrng_NPI and tot_srvcs
    data = filtered_data.groupby('Rndrng_NPI').agg({'Tot_Srvcs': 'sum'}).reset_index()

    # Rename Tot_Srvcs to Tot_stages because if you add 17311 and 17322 procedures it is the total number of stages done
    data['Tot_Stages'] = data['Tot_Srvcs']
    newdata = data_17311.groupby('Rndrng_NPI').agg({'Tot_Srvcs': 'sum'}).reset_index()

    # Use the table data_17311 and add the total number of 17311 procedures done by each doctor to the table
    data['Tot_Srvcs'] = data.apply(lambda row: newdata.loc[newdata['Rndrng_NPI'] == row['Rndrng_NPI'], 'Tot_Srvcs'].values[0] if row['Rndrng_NPI'] in newdata['Rndrng_NPI'].values else row['Tot_Srvcs'], axis=1)

    # Calculate excisions per mohs
    data['Excisions_per_Mohs'] = data['Tot_Stages']/data['Tot_Srvcs']

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
def create_histogram():    
    mean_value = data['Excisions_per_Mohs'].mean()
    plt.hist(data['Excisions_per_Mohs'], bins=30, range=(1, 4), color='lightblue', edgecolor='black')
    plt.axvline(mean_value, color='red', linestyle='dashed', label=f'Mean: {mean_value:.2f}')
    plt.xlabel('Mean Number of Stages per Procedure')
    plt.ylabel('Number of Physicians')
    plt.ylim(0, 500)
    plt.legend()
    plt.show()

def create_heat_map():
    mohs_physicians = pd.merge(data, physicians, on='Rndrng_NPI', how='inner')
    state_average = mohs_physicians.groupby('Rndrng_Prvdr_State_Abrvtn')['Excisions_per_Mohs'].mean().reset_index()
    state_count = mohs_physicians['Rndrng_Prvdr_State_Abrvtn'].value_counts().reset_index()
    state_count.columns = ['Rndrng_Prvdr_State_Abrvtn', 'state_count']

    # Load US states shapefile
    us_states = gpd.read_file("shapefiles/cb_2018_us_state_500k.shp")

    # Merge data with the shapefile
    us_states = us_states.merge(state_average, how='left', left_on='STUSPS', right_on='Rndrng_Prvdr_State_Abrvtn')

    # Create main plot for continental US
    fig, ax = plt.subplots(1, 1, figsize=(20, 10))
    us_states[~us_states['STUSPS'].isin(['HI', 'AK', 'PR', 'VI', 'GU', 'MP', 'AS'])].plot(column='Excisions_per_Mohs', cmap='Blues', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
    ax.set_title('Figure 2. Average Excisions per Mohs Procedure by State in 2021', fontsize=14, fontweight='bold') 

    # Create inset for Alaska
    ax_ak = fig.add_axes([0.0, -0.25, 1, 1])  # position and size of the inset (left, bottom, width, height)
    us_states[us_states['STUSPS'] == 'AK'].plot(column='Excisions_per_Mohs', linewidth=0.8, ax=ax_ak, edgecolor='0.8', color = (194/255, 217/255, 235/255))  # custom color for Alaska light blue

    # Create inset for Hawaii
    ax_hi = fig.add_axes([-0.15, 0.1, 0.5, 0.5])  # position and size of the inset (left, bottom, width, height)
    us_states[us_states['STUSPS'] == 'HI'].plot(column='Excisions_per_Mohs', linewidth=0.8, ax=ax_hi, edgecolor='0.8', color = (30/255, 94/255, 168/255))  # custom color for Hawaii medium-dark blue

    ax.axis('off')
    ax_ak.axis('off')
    ax_hi.axis('off')

    plt.show()


def create_line_graph(folder_path):
    """
    Create a line graph showing the mean stages per Mohs procedure over the years.

    Parameters:
    - folder_path (str): The path to the folder containing the CSV files.

    Returns:
    - None
    """

    # Get the list of CSV files in the folder
    csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

    # Initialize an empty list to store the data frames
    dfs = []

    # Read each CSV file and add the 'year' column
    for file in csv_files:
        year = file[-8:-4]  # Extract the year from the file name
        df = pd.read_csv(os.path.join(folder_path, file))
        df['year'] = year
        dfs.append(df)

    # Combine all data frames into one large data frame
    combined_df = pd.concat(dfs)
    df_17311 = combined_df[combined_df['HCPCS_Cd'].isin([17311])]

    # Filter the combined data frame by HCPCS_Cd values 17311 and 17312
    filtered_df = combined_df[combined_df['HCPCS_Cd'].isin([17311, 17312])]
    doctors_to_remove = filtered_df.loc[(filtered_df['HCPCS_Cd'] == 17311) & (filtered_df['Tot_Srvcs'] < 20), 'Rndrng_NPI'].tolist()
    filtered_df = filtered_df[~filtered_df['Rndrng_NPI'].isin(doctors_to_remove)]

    # Group filtered data by doctor and year, and calculate the sum of Tot_Srvcs
    data = filtered_df.groupby(['Rndrng_NPI', 'year']).agg({'Tot_Srvcs': 'sum'}).reset_index()
    data['Tot_Stages'] = data['Tot_Srvcs']  # Rename Tot_Srvcs to Tot_Stages
    newdata = df_17311.groupby(['Rndrng_NPI', 'year']).agg({'Tot_Srvcs': 'sum'}).reset_index()
    data['Tot_Srvcs'] = data.apply(lambda row: newdata.loc[(newdata['Rndrng_NPI'] == row['Rndrng_NPI']) & (newdata['year'] == row['year']), 'Tot_Srvcs'].values[0] if (row['Rndrng_NPI'] in newdata['Rndrng_NPI'].values) and (row['year'] in newdata['year'].values) else row['Tot_Srvcs'], axis=1)
    data['Excisions_per_Mohs'] = data['Tot_Stages'] / data['Tot_Srvcs']  # Calculate excisions per Mohs

    # Calculate the mean stages per Mohs procedure for each year
    mean_excisions_per_year = data.groupby('year')['Excisions_per_Mohs'].mean().round(2)
    years = mean_excisions_per_year.index
    values = mean_excisions_per_year.values

    # Create a line graph
    plt.plot(years, values, marker='o')
    plt.xlabel('Year')
    plt.ylabel('Mean Stages per Mohs Procedure')
    plt.ylim(1.5, 1.8)
    plt.xticks(years)
    plt.show()

create_line_graph('data')
create_heat_map()
create_histogram()

