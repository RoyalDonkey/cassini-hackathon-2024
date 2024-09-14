import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import pandas as pd
from shapely.geometry import Point, Polygon, mapping
from shapely.ops import unary_union
import json

# Load CSV data
df = pd.read_csv("data.csv")

# Function to create polygons from points (you can adjust for more irregular shapes)
def create_polygon_from_points(points):
    buffer_size = 1  # Adjust the buffer to create a larger area
    point_geometries = [Point(lon, lat).buffer(buffer_size) for lat, lon in points]
    return unary_union(point_geometries)

# Convert polygons to GeoJSON format
def polygons_to_geojson(polygons, color):
    geo_json = {
        "type": "Feature",
        "geometry": mapping(polygons),
        "properties": {"style": {"color": color, "fillColor": color, "fillOpacity": 0.4}}
    }
    return {"type": "FeatureCollection", "features": [geo_json]}

# Dash app setup
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            [
                dbc.Col(
                    # Left side for controls
                    [
                        html.H1("Europe Map: Wind and Heat Affected Areas Over Time"),
                        
                        dcc.Checklist(
                            id='effects',
                            options=[
                                {'label': 'Wind Affected Areas', 'value': 'wind'},
                                {'label': 'Heat Affected Areas', 'value': 'heat'}
                            ],
                            value=[],
                            style={'margin-bottom': '20px'}
                        ),
                        
                        dcc.Slider(
                            id='year-slider',
                            min=1970,
                            max=2100,
                            step=10,
                            marks={i: str(i) for i in range(1970, 2101, 10)},
                            value=1970,
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                        
                        html.Div(id='region-info')  # This div will show characteristics of the clicked region
                    ],
                    width=4  # Occupy 4/12 of the screen for controls
                ),
                dbc.Col(
                    # Right side for the map
                    dl.Map(
                        [dl.TileLayer(id="base-layer")],
                        id='map',
                        center=[54, 15],  # Center the map on Europe
                        zoom=4,  # Zoom in on Europe
                        maxBounds=[[35, -10], [70, 40]],  # Boundaries for Europe (latitude and longitude)
                        style={'height': '600px', 'width': '100%'}
                    ),
                    width=8  # Occupy 8/12 of the screen for the map
                )
            ]
        )
    ]
)

@app.callback(
    Output('map', 'children'),
    [Input('effects', 'value'), Input('year-slider', 'value')]
)
def update_map(effects, year):
    layers = [dl.TileLayer(id="base-layer")]
    
    # Filter data based on the selected year
    filtered_df = df[df['time'] == year]

    # If wind is selected, generate wind-affected areas
    if 'wind' in effects:
        wind_points = filtered_df[filtered_df['wind'] == 1][['latitude', 'longitude']].values
        if len(wind_points) > 0:
            wind_polygon = create_polygon_from_points(wind_points)
            wind_geojson = polygons_to_geojson(wind_polygon, 'blue')  # Set the color to blue for wind
            layers.append(dl.GeoJSON(data=wind_geojson, id='wind-layer'))

    # If heat is selected, generate heat-affected areas
    if 'heat' in effects:
        heat_points = filtered_df[filtered_df['heat'] == 1][['latitude', 'longitude']].values
        if len(heat_points) > 0:
            heat_polygon = create_polygon_from_points(heat_points)
            heat_geojson = polygons_to_geojson(heat_polygon, 'red')  # Set the color to red for heat
            layers.append(dl.GeoJSON(data=heat_geojson, id='heat-layer'))

    return layers

@app.callback(
    Output('region-info', 'children'),
    [Input('map', 'clickData')]
)
def display_region_info(clickData):
    # Debug print
    print(f"Click data: {clickData}")
    
    # Check for valid clickData
    if not clickData or 'latlng' not in clickData:
        return "Click on a region to see characteristics across years."

    try:
        # Extract latitude and longitude
        click_lat = clickData['latlng']['lat']
        click_lng = clickData['latlng']['lng']
        click_point = Point(click_lng, click_lat)

        # Initialize list to store region characteristics
        region_characteristics = []

        # Check wind-affected areas
        wind_points = df[df['wind'] == 1][['latitude', 'longitude']].values
        wind_polygon = create_polygon_from_points(wind_points)
        if wind_polygon.contains(click_point):
            wind_data = df[df['wind'] == 1].groupby('time').size().reset_index(name='count')
            region_characteristics.append(html.H4("Wind-Affected Region Characteristics Over Time"))
            region_characteristics.append(dcc.Graph(
                figure={
                    'data': [{'x': wind_data['time'], 'y': wind_data['count'], 'type': 'line', 'name': 'Wind Events'}],
                    'layout': {'title': 'Wind-Affected Region'}
                }
            ))

        # Check heat-affected areas
        heat_points = df[df['heat'] == 1][['latitude', 'longitude']].values
        heat_polygon = create_polygon_from_points(heat_points)
        if heat_polygon.contains(click_point):
            heat_data = df[df['heat'] == 1].groupby('time').size().reset_index(name='count')
            region_characteristics.append(html.H4("Heat-Affected Region Characteristics Over Time"))
            region_characteristics.append(dcc.Graph(
                figure={
                    'data': [{'x': heat_data['time'], 'y': heat_data['count'], 'type': 'line', 'name': 'Heat Events'}],
                    'layout': {'title': 'Heat-Affected Region'}
                }
            ))

        if not region_characteristics:
            return "No data available for the clicked location."

        return region_characteristics
    except Exception as e:
        # Handle any exceptions and return the error message
        return f"An error occurred: {str(e)}"

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
