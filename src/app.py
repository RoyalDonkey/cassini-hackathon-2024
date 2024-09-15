import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import pandas as pd
from shapely.geometry import Point, Polygon, mapping
from shapely.ops import unary_union
import json


df = pd.read_csv("file.csv")

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

def get_coords(year, min_mean_t = -273.15, max_mean_t = 273.15):  # KELWIN !!!
    return df[(df.time == year) & (df.mean_t > min_mean_t) & (df.mean_t < max_mean_t)][['lat', 'lon']].values

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
    html.Div([
        html.Div([
            html.Img(src='/assets/logo2.png',
                    style={
                    'height': '60px', 'width': '70px'
                }),
            html.Div('Purrfect Places', style={'fontSize': 40, 'color': '#447F00', 'font-weight': 'bold', 'height': '60px', 'text-align': 'bottom'})
        ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-around', 'padding': '10px'}),
        html.Div([
            dcc.Link('Home', href='/'),
            dcc.Link('Search Engine', href='/search'),
            dcc.Link('Map', href='/map')
        ],  style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-around', 'padding': '10px'}),

    ], style={'display': 'flex', 'flexDirection': 'column', 'padding': '10px'}),

    html.Div(id='page-content')], style={'flex': 1, 'padding': '10px'}),
    html.Div([
        dl.Map(
                        [dl.TileLayer(id="base-layer")],
                        id='map',
                        center=[54, 15],  # Center the map on Europe
                        zoom=4,  # Zoom in on Europe
                        maxBounds=[[35, -10], [70, 40]],  # Boundaries for Europe (latitude and longitude)
                        style={'height': '600px', 'width': '100%'}
                    )        
    ], style={'flex': 2, 'padding': '10px'})
], style={'display': 'flex', 'flexDirection': 'row', 'padding': '10px'})

# Define the layout for each page
page_layouts = {
    '/': html.Div([
        html.Div('Welcome to the future', style={'fontSize': 24, 'textAlign': 'center'}),
        html.Div('bla bla opis', style={'fontSize': 18, 'textAlign': 'center', 'marginTop': '10px'})
    ]),

    '/search': html.Div([
        html.Div([
            html.Div([
                html.H3('Requirements:'),
                html.Div([
                    dcc.Input(id='year-input', type='number', placeholder='Year'),
                    html.Div([
                        html.Div('Temperature: '),
                        dcc.Input(id='temp-min-input', type='number', placeholder='Minimal'),
                        html.Div(' - '),
                        dcc.Input(id='temp-max-input', type='number', placeholder='Maximal')
                    ], style={'display': 'flex', 'flexDirection': 'row'})
                    
                ], style={'display': 'flex', 'flexDirection': 'column'})
            ], style={'padding': '10px'}),
            
            html.Div([
                html.Button('Search', id='search', n_clicks=0)
            ]),

            # Map Options
            html.Div([
                html.H3('Map options:'),
                html.Div([
                    html.Div([
                    html.Div('Visible layer: '),
                    dcc.Dropdown(id='effects', options=[
                        {'label': 'Mean Temperature', 'value': 'mean_t'},
                        {'label': 'Hot days count', 'value': 'hot_d'},
                        {'label': 'Cold days count', 'value': 'cold_d'},
                        {'label': 'Dry days count', 'value': 'droughts'}
                    ], value='', style={'flex': 1})], style={'display': 'flex', 'flexDirection': 'row', 'width': '100%', 'alignItems': 'center'}),
                    # html.Div([
                    #     html.Div('Visible year: '),
                    #      html.Div([
                    #         dcc.Slider(
                    #             id='year-slider',
                    #             min=1970,
                    #             max=2100,
                    #             step=10,
                    #             marks={i: str(i) for i in range(1970, 2101, 25)},
                    #             value=1970,
                    #             tooltip={"placement": "bottom", "always_visible": True}
                    #         )
                    #     ], style={'flex': 1})], 
                    #     style={'display': 'flex', 'flexDirection': 'row', 'width': '100%', 'alignItems': 'center'})
                ], style={'display': 'flex', 'flexDirection': 'column', 'padding': '10px', 'width': '100%'}),
            ], style={'width': '100%'})
            
        ], style={'display': 'flex', 'height': '300px', 'width': '100%', 'flexDirection': 'column'}),

        html.Div([
            html.Div(id='region-info')
        ], style={'display': 'flex', 'height': '200px', 'width': '100%', 'flexDirection': 'row'})
    ]),

    '/map': html.Div([
        html.Div([
                html.H3('Map options:'),
                html.Div([
                    html.Div([
                    html.Div('Visible layer: '),
                    dcc.Dropdown(id='effects', options=[
                        {'label': 'Mean Temperature', 'value': 'mean_t'},
                        {'label': 'Hot days count', 'value': 'hot_d'},
                        {'label': 'Cold days count', 'value': 'cold_d'},
                        {'label': 'Dry days count', 'value': 'droughts'}
                    ], value='', style={'flex': 1})], style={'display': 'flex', 'flexDirection': 'row', 'width': '100%', 'alignItems': 'center'}),
                    html.Div([
                        html.Div('Visible year: '),
                         html.Div([
                            dcc.Slider(
                                id='year-slider',
                                min=1970,
                                max=2100,
                                step=10,
                                marks={i: str(i) for i in range(1970, 2101, 25)},
                                value=1970,
                                tooltip={"placement": "bottom", "always_visible": True}
                            )
                        ], style={'flex': 1})], style={'display': 'flex', 'flexDirection': 'row', 'width': '100%', 'alignItems': 'center'})
                ], style={'display': 'flex', 'flexDirection': 'column', 'padding': '10px', 'width': '100%'}),
            ], style={'width': '100%'})

    ], style={}),

    # '/point-map': html.Div([
    #     html.Div([
    #         html.Div([
    #             dcc.Dropdown(id='point-map-dropdown', options=[
    #                 {'label': 'Option 1', 'value': 'option1'},
    #                 {'label': 'Option 2', 'value': 'option2'}
    #             ], value='option1'),
    #             dcc.Slider(id='point-map-slider', min=2000, max=2020, step=1, value=2020)
    #         ], style={'flex': 1, 'borderBottom': '1px solid black', 'padding': '10px'}),

    #         html.Div([
    #             dcc.Input(id='address-input', type='text', placeholder='Enter address'),
    #             html.Button('FIND', id='find-button'),
    #             html.Div(id='address-output'),
    #             html.Div(id='address-table', style={'marginTop': '10px'})
    #         ], style={'flex': 1, 'padding': '10px'})
    #     ], style={'flex': 1, 'display': 'flex', 'flexDirection': 'column', 'borderRight': '1px solid black'}),

    #     html.Div(dcc.Graph(id='point-map-plot'), style={'flex': 3, 'padding': '10px'})
    # ], style={'display': 'flex', 'height': '500px', 'width': '100%', 'flexDirection': 'row'})
}

# Create a function to generate the map for a specific year and category
def create_map(year, category):
    # Filter the data for the selected year
    filtered_df = df[df['time'] == year]
    
    # Create the map
    fig = px.density_mapbox(
        filtered_df, 
        lat='lat', 
        lon='lon', 
        z=category, 
        radius=20, 
        center=dict(lat=50, lon=10),  # Center the map over Europe
        zoom=3, 
        mapbox_style="carto-positron",  # Use a Mapbox style
        color_continuous_scale='YlOrRd',
        title=f'{category.capitalize()} Heatmap for {year}'
    )
    return fig

# Set up the callback to update the map when the slider or dropdown changes
@app.callback(
    Output('heatmap', 'figure'),
    [Input('year-slider', 'value'), Input('category-dropdown', 'value')]
)
def update_map(selected_year, selected_category):
    return create_map(selected_year, selected_category)

# Callback to update page content based on URL
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def update_page(pathname):
    return page_layouts.get(pathname, '404 Page Not Found')


@app.callback(Output('map', 'children'),
              Input('search', 'n_clicks'),
              Input('temp-min-input', 'value'),
              Input('temp-max-input', 'value'),
              Input('year-input', 'value'))
def search_engine(search_clicks, temp_min, temp_max, year):
    layers = [dl.TileLayer(id="base-layer")]
    
    coords = get_coords(year, temp_min, temp_max)

    if len(coords) > 0:
        wind_polygon = create_polygon_from_points(coords)
        wind_geojson = polygons_to_geojson(wind_polygon, 'green')  # Set the color to blue for wind
        layers.append(dl.GeoJSON(data=wind_geojson))
    
    return layers


    

# Placeholder callbacks for tables and address lookup
@app.callback(Output('address-output', 'children'),
              [Input('find-button', 'n_clicks')],
              [Input('address-input', 'value')])
def find_address(n_clicks, address_value):
    if n_clicks and address_value:
        return f"Address found: {address_value}"
    return "Enter an address"

# Placeholder table callbacks for search engine tables
@app.callback(Output('table-left', 'children'),
              [Input('plot-dropdown', 'value')])
def update_left_table(selected_option):
    return html.Div([html.P(f"Left Table Data - {selected_option}")])

@app.callback(Output('table-right', 'children'),
              [Input('plot-dropdown', 'value')])
def update_right_table(selected_option):
    return html.Div([html.P(f"Right Table Data - {selected_option}")])


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