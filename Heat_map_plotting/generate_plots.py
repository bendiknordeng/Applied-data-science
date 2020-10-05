import pandas as pd
import geopandas
import folium as folium

# READ ME
# This file generates and saved different heat maps.
# It is important to specify the correct global parameters before generating a plot.

# decide granularity level (either bydel or delbydel)
BYDEL = True

# Data sources
if BYDEL:
    HEAT_MAP_DATA_FILE_NAME = '../Data/heat_map_bydel_plotting_values.xlsx'
    AREA_ID_COLUMN_NAME = 'Bydel_ID'
    GEO_DATA_FILE_NAME = '../Data/heat_map_bydel_boundaries.geojson'
    HOOVER_FIELD = ['Bydel_Navn']
else:
    HEAT_MAP_DATA_FILE_NAME = '../Data/heat_map_delby_plotting_values.xlsx'
    AREA_ID_COLUMN_NAME = 'Delbydel_ID'
    GEO_DATA_FILE_NAME = '../Data/heat_map_delby_boundaries.geojson'
    HOOVER_FIELD = ['Delbydel_Navn']

# Values to be plotted
HEAT_MAP_DATA_SHEET_NAMES = ['Input_inntekt']                   # ['Input_inntekt', 'Input_folketall', 'Input_befolkningstetthet_20-40']
HEAT_MAP_DATA_COLUMN_NAMES = ['Inntekt 2017']                   # ['Inntekt 2017', 'Folketall 2020', 'Befolkningstetthet_20-40']
HEAT_MAP_TITLES = ['Income Oslo 2017']                          # ['Income Oslo 2017', 'Population Oslo 2020', 'Population density Oslo']
HEAT_MAP_OUTPUT_FILE_NAMES = ['heat_map_income_5.html']         # ['Income Oslo 2017', 'Population.html', 'Population_density_20-40.html']

# Map specifications
CENTER_OF_MAP = [59.91, 10.73]
PLOTTING_COLOR = 'YlOrRd'                                         # YlGnBu, BuPu, Spectral, BrBg, Blues, Greys
PLOTTING_FILL_OPACITY = 0.3
ZOOM = 11
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
        heatMapPlot = plot(delby, ['geoid', HEAT_MAP_DATA_COLUMN_NAMES[i]], HEAT_MAP_TITLES[i], PLOTTING_COLOR,
                           PLOTTING_FILL_OPACITY)
        heatMapPlot.save('../Plots/' + HEAT_MAP_OUTPUT_FILE_NAMES[i])


def plot(data, plot_list, legend_name, colour='YlOrRd', fill_opacity=0.2):
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
    # m.geojson.add_child(folium.features.GeoJsonTooltip(HOOVER_FIELD, labels=False))
    return m

main()
