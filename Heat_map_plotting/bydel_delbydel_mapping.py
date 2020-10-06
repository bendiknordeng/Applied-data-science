import pandas as pd
import geopandas


# READ ME
# This file takes in information about delbydeler and create a large delby polygon

# configurable parameters
WRITE_GEOJSON = True
WRITE_EXCEL = True

# Read in the the separate data sources to pandas
df = pd.read_excel(r'../data/heat_map_bydeler_delbydeler_grunnkretser.xlsx', sheet_name='Table 1')
df2 = pd.read_csv(r'../data/neighbourhoods.csv')
gdf = geopandas.GeoDataFrame.from_file("../data/heat_map_grunnkretser_oslo.geojson")

# Convert object to int64
gdf['grunnkretsnummer'] = gdf['grunnkretsnummer'].astype(int)

# Merge the data based on grunnkretsnummer
df = pd.merge(df, df2, left_on='Bydel_Navn', right_on='neighbourhood')
all_data = pd.merge(gdf, df, left_on='grunnkretsnummer', right_on='grunnkretsnummer')

# Create set of dataframes
gdfs = []
for i in all_data.Bydel_ID.unique():
    new_gdf = geopandas.GeoDataFrame(all_data[all_data['Bydel_ID'] == i])
    new_gdf['geometry'] = new_gdf.unary_union
    gdfs.append(new_gdf)

# concatenate the geodataframes
all_data = pd.concat(gdfs)

# Set crs
all_data.crs = "EPSG:25832"

# Reduce the number of columns
bydel = all_data[['geometry', 'Bydel_ID', 'Bydel_Navn', "neighbourhood_group"]].copy()

# Calculate the square km per bydel
bydel['Bydel_area'] = bydel['geometry'].to_crs({'init': 'epsg:4326'}).map(lambda p: p.area / 10 ** 6)

# Calculate centroids per bydel
bydel['Bydel_centroid_longitude'] = bydel['geometry'].to_crs({'init': 'epsg:4326'}).map(lambda p: p.centroid.x)
bydel['Bydel_centroid_latitude'] = bydel['geometry'].to_crs({'init': 'epsg:4326'}).map(lambda p: p.centroid.y)


bydel.drop_duplicates(inplace=True)

# Write to a geojson format
if WRITE_GEOJSON: bydel.to_file("../data/heat_map_bydel_boundaries.geojson", driver="GeoJSON")
if WRITE_EXCEL: bydel.to_excel('../data/heat_map_bydel.xlsx')
