# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            'SpaceX Launch Records Dashboard',
            style={
                'textAlign': 'center', 
                'color': '#503D36',
                'font-size': 40
            }
        ),
        html.Br(),
        html.Div(
            [
                dcc.Dropdown(
                    id='site_select_id',
                    options=[
                        {'label': 'All Sites', 'value': 'all',},
                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40',},
                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E',},
                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A',},
                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40',},
                    ],
                    value='all',
                    # placeholder='idk',
                    searchable=True,
                ),
            ]
        ),
        html.Br(),
        html.Div(
            [
                dcc.Graph(
                    id='success_pie_chart'
                ),
            ]
        ),
        html.Br(),
        html.P(
            "Payload range (Kg):"
        ),
        html.Div(
            [
                dcc.RangeSlider(
                    id='payload_slider_id',
                    min=0, 
                    max=10000, 
                    step=1000,
                    marks={  # according to documentation, the marks should be appearing automatically, but are not without me manually setting them. /s
                        0: '0',
                        1000: '1000',
                        2000: '2000',
                        3000: '3000',
                        4000: '4000',
                        5000: '5000',
                        6000: '6000',
                        7000: '7000',
                        8000: '8000',
                        9000: '9000',
                        10000: '10000',
                    },
                    value=[
                        2000, 
                        8000
                    ]
                )
            ]
        ),
        html.Br(), 
        html.Div(
            [
                dcc.Graph(
                    id='success_payload_scatter_chart'
                )
            ]
        ),
    ]
)

@app.callback(
    Output(component_id='success_pie_chart', component_property='figure'),
    Input(component_id='site_select_id', component_property='value'), 
)
def get_pie_chart(entered_site):
    if entered_site == 'all':
        fig = px.pie(
            data_frame=spacex_df, 
            values='class', 
            names='Launch Site', 
            title='Total Successes by Launch Site'
        )  
        return fig
    else: 
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]['class'].value_counts().sort_index().to_frame()
        fig = px.pie(
            data_frame=filtered_df,  # check, value_counts might be bad behavior with bad ordering due to counts and order of first occurence  
            values='class', 
            names=filtered_df.index.values.tolist(), 
            color='class', 
            title=f"Total Success Launches for site {entered_site}"
        )
        fig.update_traces(sort=False)  # without this, the KSC LC-39A launch site pie chart will have a different order in the slices and legend. I am unsure why other than it auto orders them based on size. 
        # but according to doumentation "By default, Plotly Express lays out legend items in the order in which values appear in the underlying data." https://plotly.com/python/legend/ 
        # maybe because that is specific to the legend? and what i'm dealing with are traces or something? 
        # what are traces? 
        '''
        print(entered_site)
        print(spacex_df[spacex_df['Launch Site'] == entered_site]['class'])
        print(filtered_df)
        print(filtered_df.index)
        print(filtered_df.index.values)
        print(filtered_df.index.values.tolist())
        '''
        return fig


@app.callback(
    [
        Output(component_id='success_payload_scatter_chart', component_property='figure'), 
    ],
    [
        Input(component_id='site_select_id', component_property='value'), 
        Input(component_id="payload_slider_id", component_property="value"), 
    ],
)
def get_scatter_plot(entered_site, payload_slider):
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_slider[0]) & (spacex_df['Payload Mass (kg)'] <= payload_slider[1])]
    if entered_site == 'all':
        title='Correlation between Payload and Success for all Sites'
    else: 
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        title=f"Correclation between Payload and Success for {entered_site}"
    fig = px.scatter(
        data_frame=filtered_df, 
        x='Payload Mass (kg)',
        y='class', 
        color='Booster Version Category', 
        title=title
    ) 
    return [fig]  # needs to be a list because Output compoenent is in a list? neat. 


# Run the app
if __name__ == '__main__':
    app.run_server()