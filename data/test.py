import geopandas
from fiona.crs import from_epsg


df = geopandas.GeoDataFrame.from_file("../data/neighbourhoods.geojson")
df.info()

gdf = df['geometry'].explode()
gdf.crs = "EPSG:4326"

# Calculate the square km per gdf
df['gdf_area'] = df['geometry'].to_crs({'init': 'epsg:4326'}).map(lambda p: p.area / 10 ** 6)

# Calculate centroids per gdf
df['gdf_centroid_longitude'] = df['geometry'].to_crs({'init': 'epsg:4326'}).map(lambda p: p.centroid.x)
df['gdf_centroid_latitude'] = df['geometry'].to_crs({'init': 'epsg:4326'}).map(lambda p: p.centroid.y)



gdf.drop_duplicates(inplace=True)

gdf = gdf.to_crs(epsg=25832)
print(gdf)
print(gdf.info())

gdf.to_file("../data/heat_map_bydel_boundaries_2.geojson", driver="GeoJSON")

