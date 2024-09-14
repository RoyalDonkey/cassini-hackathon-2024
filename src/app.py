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


df = pd.read_csv("data/file.csv")

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

# Create a sample dataframe for demonstration
np.random.seed(0)
years = np.arange(2000, 2021)
temperature = np.random.uniform(0, 100, size=len(years))
df = pd.DataFrame({'Year': years, 'Temperature': temperature})

# Create a sample plot
def create_plot(selected_option, year_slider_value):
    filtered_df = df[df['Year'] <= year_slider_value]
    fig = px.line(filtered_df, x='Year', y='Temperature', title=f'{selected_option} over Years')
    return fig

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
            html.Div('Cat4Green', style={'fontSize': 40, 'color': '#447F00', 'font-weight': 'bold', 'height': '60px', 'text-align': 'bottom'})
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
                    ),
        dcc.Dropdown(id='effects', options=[
                {'label': 'Wind Affected Areas', 'value': 'wind'},
                {'label': 'Heat Affected Areas', 'value': 'heat'}
            ], value=''),
        dcc.Slider(
                    id='year-slider',
                    min=1970,
                    max=2100,
                    step=10,
                    marks={i: str(i) for i in range(1970, 2101, 10)},
                    value=1970,
                    tooltip={"placement": "bottom", "always_visible": True}
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
                html.H3('Search Engine'),
                html.Div([
                    dcc.Input(id='year-input', type='number', placeholder='Year'),
                    dcc.Input(id='temp-input', type='number', placeholder='Temperature')
                ], style={'display': 'flex', 'flexDirection': 'column'})
            ], style={'flex': 1, 'padding': '10px'}),  # Reduced width for input section

            html.Div([
                dcc.Dropdown(id='plot-dropdown', options=[
                    {'label': 'Temperature', 'value': 'Temperature'}
                ], value='Temperature'),
                dcc.Slider(id='year-slider', min=2000, max=2020, step=1, value=2020),
                dcc.Graph(id='random-plot')
            ], style={'flex': 2, 'padding': '10px'})  # Reduced plot width to prevent overlap
        ], style={'display': 'flex', 'height': '300px', 'width': '100%', 'flexDirection': 'row'}),

        html.Div([
            html.Div(id='table-left', style={'flex': 1, 'padding': '10px', 'border': '1px solid black'}),  # Left table
            html.Div(id='table-right', style={'flex': 1, 'padding': '10px', 'border': '1px solid black'})  # Right table
        ], style={'display': 'flex', 'height': '200px', 'width': '100%', 'flexDirection': 'row'})  # Increased table height
    ]),

    '/map': html.Div([
        html.Div([
            dcc.Dropdown(id='effects', options=[
                {'label': 'Wind Affected Areas', 'value': 'wind'},
                {'label': 'Heat Affected Areas', 'value': 'heat'}
            ], value=''),
            dcc.Slider(
                        id='year-slider',
                        min=1970,
                        max=2100,
                        step=10,
                        marks={i: str(i) for i in range(1970, 2101, 10)},
                        value=1970,
                        tooltip={"placement": "bottom", "always_visible": True}
                    ),
            html.Div(id='region-info')
        ], style={'padding': '10px'}),

    ], style={'height': '500px', 'width': '100%'}),

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

# Callback to update page content based on URL
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def update_page(pathname):
    return page_layouts.get(pathname, '404 Page Not Found')

# Callback for the plot on the search page
@app.callback(Output('random-plot', 'figure'),
              Input('plot-dropdown', 'value'),
              Input('year-slider', 'value'))
def update_plot(selected_option, year_slider_value):
    return create_plot(selected_option, year_slider_value)

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

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
