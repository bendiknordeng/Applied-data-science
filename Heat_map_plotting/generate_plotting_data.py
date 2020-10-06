import pandas as pd
import numpy as np

INPUT_DATA_PATH = '../Data/listings.csv'
OUTPUT_DATA_PATH = '../Data/heat_map_bydel_plotting_values_test.xlsx'
BYDEL_DATA_PATH = '../Data/heat_map_bydel.xlsx'

# Read in the data
df = pd.read_csv(INPUT_DATA_PATH)
df2 = pd.read_excel(BYDEL_DATA_PATH)

# Show some information about the data
df.info()

# Create df where all aggregated data will be placed
aggregated_df = pd.DataFrame()

# Generate general data for each neighbourhood (decrease granularity)
aggregated_df['mean_price'] = df.groupby(by="neighbourhood")['price'].agg(np.mean)
aggregated_df['mean_min_nights'] = df.groupby(by="neighbourhood")['minimum_nights'].agg(np.mean)
aggregated_df['neighbourhood'] = aggregated_df.index

# Merge the input data to get Bydel_ID
aggregated_df = pd.merge(aggregated_df, df2, left_on='neighbourhood', right_on='Bydel_Navn', )

# Write data to Excel file
aggregated_df.to_excel(OUTPUT_DATA_PATH)
