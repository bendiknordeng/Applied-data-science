import pandas as pd
import geopandas
import folium as folium
from shapely.geometry import Point
from folium.plugins import FloatImage

# READ ME
# This file generates and saved different heat maps.
# It is important to specify the correct global parameters before generating a plot.

# decide granularity level (either bydel or delbydel)
BYDEL = True

# Data sources
LISTINGS = '../Data/listings_detailed.csv'
if BYDEL:
    HEAT_MAP_DATA_FILE_NAME = '../Data/heat_map_bydel_plotting_values_test.xlsx'
    AREA_ID_COLUMN_NAME = 'Bydel_ID'
    GEO_DATA_FILE_NAME = '../Data/heat_map_bydel_boundaries.geojson'
    HOOVER_FIELD = ['Bydel_Navn', 'mean_price']
    ALIASES = ['Neighbourhood: ', 'Mean price: ']
else:
    HEAT_MAP_DATA_FILE_NAME = '../Data/heat_map_delby_plotting_values.xlsx'
    AREA_ID_COLUMN_NAME = 'Delbydel_ID'
    GEO_DATA_FILE_NAME = '../Data/heat_map_delby_boundaries.geojson'
    HOOVER_FIELD = ['Delbydel_Navn', 'mean_price']

# Values to be plotted
HEAT_MAP_DATA_SHEET_NAMES = ['Sheet1']                   # ['Input_inntekt', 'Input_folketall', 'Input_befolkningstetthet_20-40']
HEAT_MAP_DATA_COLUMN_NAMES = ['mean_price']                   # ['Inntekt 2017', 'Folketall 2020', 'Befolkningstetthet_20-40']
HEAT_MAP_TITLES = ['Mean price AirBnB']                          # ['Income Oslo 2017', 'Population Oslo 2020', 'Population density Oslo']
HEAT_MAP_OUTPUT_FILE_NAMES = ['mean_price_AirBnB.html']         # ['Income Oslo 2017', 'Population.html', 'Population_density_20-40.html']

# Map specifications
CENTER_OF_MAP = [59.91, 10.73]
PLOTTING_COLOR = ['YlOrRd']                                     # YlGnBu, BuPu, Spectral, BrBg, Blues, Greys
PLOTTING_FILL_OPACITY = 0.3
ZOOM = 12
TILES = 'cartodbpositron'


def main():
    # Read in the the separate data sources to pandas and merge data sources
    delby = geopandas.GeoDataFrame.from_file(GEO_DATA_FILE_NAME)
    for i in range(len(HEAT_MAP_DATA_SHEET_NAMES)):
        heatMapData = pd.read_excel(HEAT_MAP_DATA_FILE_NAME, sheet_name=HEAT_MAP_DATA_SHEET_NAMES[i]).loc[:,
                      [AREA_ID_COLUMN_NAME] + [HEAT_MAP_DATA_COLUMN_NAMES[i]]]
        delby = pd.merge(delby, heatMapData, left_on=AREA_ID_COLUMN_NAME, right_on=AREA_ID_COLUMN_NAME)

    # Create a Geo-id which is needed by the Folium (it needs to have a unique identifier for each row)
    delby['geoid'] = delby.index.astype(str)

    # Ensure correct epsg
    delby.crs = "EPSG:25832"

    # Plot heat map data
    for i in range(len(HEAT_MAP_DATA_SHEET_NAMES)):
        heatMapPlot = plot(delby, ['geoid', HEAT_MAP_DATA_COLUMN_NAMES[i]], HEAT_MAP_TITLES[i], PLOTTING_COLOR[i],
                           PLOTTING_FILL_OPACITY)
        heatMapPlot.save('../Plots/' + HEAT_MAP_OUTPUT_FILE_NAMES[i])

    # Plot listings
    listings_map = plot_listings()
    listings_map.save('../Plots/cluster_listing.html')


def plot(data, plot_list, legend_name, colour, fill_opacity=0.2):
    # Create a Map instance
    m = folium.Map(location=CENTER_OF_MAP, tiles=TILES, zoom_start=ZOOM, control_scale=True)

    # Plot the extra layer of information for each delbydel
    m = folium.Choropleth(
        geo_data=data,
        name=plot_list[1],
        data=data,
        columns=plot_list,
        key_on='feature.id',
        fill_color=colour,  # YlGnBu, BuPu, Spectral, BrBg, Blues, Greys
        fill_opacity=fill_opacity,
        line_opacity=0.2,
        line_color='white',
        line_weight=0,
        highlight=False,
        smooth_factor=1.0,
        legend_name=legend_name).add_to(m)
    folium.LayerControl().add_to(m)

    # Display Region Label
    m.geojson.add_child(folium.features.GeoJsonTooltip(fields=HOOVER_FIELD, aliases=ALIASES, labels=True))
    return m


def plot_listings():
    df = pd.read_csv(LISTINGS)
    locs_geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
    crs = {'init': 'epsg:4326'}
    # Coordinate Reference Systems, "epsg:4326" is a common projection of WGS84 Latitude/Longitude
    locs_gdf = geopandas.GeoDataFrame(df, crs=crs, geometry=locs_geometry)
    m = folium.Map(location=[59.91, 10.73], zoom_start=10, tiles='cartodbpositron')

    feature_ea = folium.FeatureGroup(name='Entire home/apt')
    feature_pr = folium.FeatureGroup(name='Private room')

    for i, v in locs_gdf.iterrows():
        hoover_text = """
        Price: <b>%s</b><br>
        Minimum nights: <b>%s</b><br>
        URL: <b>%s</b><br>
        """ % (v['price'], v['minimum_nights'], v['listing_url'])
        popup_text ="Price: %s \nMinimum nights: %s \nURL: %s" % (v['price'], v['minimum_nights'], v['listing_url'])
        popup = folium.Popup(popup_text, parse_html=True)

        if v['room_type'] == 'Entire home/apt':
            folium.CircleMarker(location=[v['latitude'], v['longitude']],
                                radius=5,
                                tooltip=hoover_text,
                                popup=popup,
                                color='#FFBA00',
                                fill_color='#FFBA00',
                                fill=True).add_to(feature_ea)
        elif v['room_type'] == 'Private room':
            folium.CircleMarker(location=[v['latitude'], v['longitude']],
                                radius=5,
                                tooltip=hoover_text,
                                popup=popup,
                                color='#087FBF',
                                fill_color='#087FBF',
                                fill=True).add_to(feature_pr)
    feature_ea.add_to(m)
    feature_pr.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    return m

main()
