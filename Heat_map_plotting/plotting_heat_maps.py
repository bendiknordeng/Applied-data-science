from folium import plugins
import pandas as pd
import geopandas
import folium as folium
from shapely.geometry import Point

# READ ME
# This file plots different heat maps and saves them to file

# configurable parameters
HEAT_MAP_DATA_FILE_NAME = '../Data/heat_map_plotting_values.xlsx'
AREA_ID_COLUMN_NAME = 'Delbydel_ID'
GEO_DATA_FILE_NAME = '../Data/heat_map_delby_boundaries.geojson'
HEAT_MAP_DATA_SHEET_NAMES = ['Input_folketall']                   # ['Input_inntekt', 'Input_folketall', 'Input_befolkningstetthet_20-40']
HEAT_MAP_DATA_COLUMN_NAMES = ['Folketall 2020']                   # ['Inntekt 2017', 'Folketall 2020', 'Befolkningstetthet_20-40']
HEAT_MAP_TITLES = ['Population Oslo 2020']                        # ['Income Oslo 2017', 'Population Oslo 2020', 'Population density Oslo']
HEAT_MAP_OUTPUT_FILE_NAMES = ['heat_map_population.html']         # ['Income.html', 'Population.html', 'Population_density_20-40.html']
PLOTTING_COLOR = 'YlOrRd'                                         # YlGnBu, BuPu, Spectral, BrBg, Blues, Greys
PLOTTING_FILL_OPACITY = 0.3


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
        heatMapPlot = plot(delby, ['geoid', HEAT_MAP_DATA_COLUMN_NAMES[i]], HEAT_MAP_TITLES[i], PLOTTING_COLOR,
                           PLOTTING_FILL_OPACITY)
        heatMapPlot.save('../Plots/' + HEAT_MAP_OUTPUT_FILE_NAMES[i])

    """
    # Plot one concept
    m6 = plot_one_concept(delby, ['geoid', 'Folketall 2020'], "Population", 'YlGnBu')
    m6.save('../Plots/Hairdressers.html')
    """
    """
    # Plot concepts
    m4 = plot_concepts()
    m4.save('../plots/heat_map_concepts.html')
    """
    """
    # Plot clusters
    m5 = plot_clusters()
    m5.save('../plots/heat_map_cluster.html')
    """

def plot(data, plot_list, legend_name, colour='YlOrRd', fill_opacity=0.2):
    # Create a Map instance
    m = folium.Map(location=[59.91, 10.73], tiles='cartodbpositron', zoom_start=11, control_scale=True)

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
    m.geojson.add_child(folium.features.GeoJsonTooltip(['Delbydel_Navn'], labels=False))
    return m


def plot_clusters():
    df = pd.read_excel(r'../Data/heat_map_cluster_values.xlsx')
    locs_geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
    crs = {'init': 'epsg:4326'}
    # Coordinate Reference Systems, "epsg:4326" is a common projection of WGS84 Latitude/Longitude
    locs_gdf = geopandas.GeoDataFrame(df, crs=crs, geometry=locs_geometry)
    m = folium.Map(location=[59.91, 10.73], zoom_start=10, tiles='cartodbpositron')
    marker_cluster = plugins.MarkerCluster().add_to(m)

    for i, v in locs_gdf.iterrows():
        popup = """
        Address: <b>%s</b><br>
        Company name : <b>%s</b><br>
        """ % (v['Adresse'], v['Navn'])

        if v['Konsept'] == '3.1.1 Groceries':
            folium.CircleMarker(location=[v['latitude'], v['longitude']],
                                radius=5,
                                tooltip=popup,
                                color='#FFBA00',
                                fill_color='#FFBA00',
                                fill=True).add_to(marker_cluster)
        elif v['Konsept'] == '2.4 Pub':
            folium.CircleMarker(location=[v['latitude'], v['longitude']],
                                radius=5,
                                tooltip=popup,
                                color='#087FBF',
                                fill_color='#087FBF',
                                fill=True).add_to(marker_cluster)
        elif v['Konsept'] == '4.2.2 Body treatment':
            folium.CircleMarker(location=[v['latitude'], v['longitude']],
                                radius=5,
                                tooltip=popup,
                                color='#FF0700',
                                fill_color='#FF0700',
                                fill=True).add_to(marker_cluster)
    return m


def plot_concepts():
    df = pd.read_excel(r'../Data/heat_map_cluster_values.xlsx')
    locs_geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
    crs = {'init': 'epsg:4326'}
    # Coordinate Reference Systems, "epsg:4326" is a common projection of WGS84 Latitude/Longitude
    locs_gdf = geopandas.GeoDataFrame(df, crs=crs, geometry=locs_geometry)
    m = folium.Map(location=[59.91, 10.73], zoom_start=10, tiles='cartodbpositron')

    feature_ea = folium.FeatureGroup(name='3.1.1 Groceries')
    feature_pr = folium.FeatureGroup(name='2.4 Pub')
    feature_sr = folium.FeatureGroup(name='4.2.2 Body treatment')

    for i, v in locs_gdf.iterrows():
        popup = """
        Address: <b>%s</b><br>
        Company name : <b>%s</b><br>
        """ % (v['Adresse'], v['Navn'])

        if v['Konsept'] == '3.1.1 Groceries':
            folium.CircleMarker(location=[v['latitude'], v['longitude']],
                                radius=5,
                                tooltip=popup,
                                color='#FFBA00',
                                fill_color='#FFBA00',
                                fill=True).add_to(feature_ea)
        elif v['Konsept'] == '2.4 Pub':
            folium.CircleMarker(location=[v['latitude'], v['longitude']],
                                radius=5,
                                tooltip=popup,
                                color='#087FBF',
                                fill_color='#087FBF',
                                fill=True).add_to(feature_pr)
        elif v['Konsept'] == '4.2.2 Body treatment':
            folium.CircleMarker(location=[v['latitude'], v['longitude']],
                                radius=5,
                                tooltip=popup,
                                color='#FF0700',
                                fill_color='#FF0700',
                                fill=True).add_to(feature_sr)
    feature_ea.add_to(m)
    feature_pr.add_to(m)
    feature_sr.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    return m


def plot_one_concept(data, plot_list, legend_name, colour='YlOrRd', fill_opacity=0.2):
    df = pd.read_excel(r'../Data/heat_map_cluster_values.xlsx')
    locs_geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
    crs = {'init': 'epsg:4326'}
    # Coordinate Reference Systems, "epsg:4326" is a common projection of WGS84 Latitude/Longitude
    locs_gdf = geopandas.GeoDataFrame(df, crs=crs, geometry=locs_geometry)
    m = folium.Map(location=[59.91, 10.73], zoom_start=10, tiles='cartodbpositron')

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

    feature_ea = folium.FeatureGroup(name='4.2.1 Hairdresser')

    for i, v in locs_gdf.iterrows():
        popup = """
        Address: <b>%s</b><br>
        Company name : <b>%s</b><br>
        """ % (v['Adresse'], v['Navn'])

        if v['Konsept'] == '4.2.1 Hairdresser':
            folium.CircleMarker(location=[v['latitude'], v['longitude']],
                                radius=5,
                                tooltip=popup,
                                color='#FF0700',
                                fill_color='#FF0700',
                                fill=True).add_to(feature_ea)
    feature_ea.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    # Display Region Label
    m.geojson.add_child(folium.features.GeoJsonTooltip(['Delbydel_Navn'], labels=False))
    return m

main()
