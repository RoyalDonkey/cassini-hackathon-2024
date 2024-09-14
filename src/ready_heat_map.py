import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv('data/filtered_data.csv')

# Set up the Dash app
app = dash.Dash(__name__)

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

# Define the layout with a slider, dropdown, and a map
app.layout = html.Div([
    html.H1('Climate Data Heatmap Over the Years'),
    dcc.Dropdown(
        id='category-dropdown',
        options=[
            {'label': 'Mean Temperature', 'value': 'mean_t'},
            {'label': 'Hot Days', 'value': 'hot_d'},
            {'label': 'Cold Days', 'value': 'cold_d'},
            {'label': 'Droughts', 'value': 'droughts'}
        ],
        value='droughts',  # Default value
        clearable=False
    ),
    dcc.Slider(
        id='year-slider',
        min=df['time'].min(),
        max=df['time'].max(),
        value=df['time'].min(),
        marks={str(year): str(year) for year in df['time'].unique()},
        step=None
    ),
    dcc.Graph(id='heatmap')
])

# Set up the callback to update the map when the slider or dropdown changes
@app.callback(
    Output('heatmap', 'figure'),
    [Input('year-slider', 'value'), Input('category-dropdown', 'value')]
)
def update_map(selected_year, selected_category):
    return create_map(selected_year, selected_category)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
