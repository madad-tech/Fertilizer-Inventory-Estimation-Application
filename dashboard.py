import dash
from dash import dash_table
from dash.dependencies import Input, Output, State
from dash import html,dcc
import yaml
import plotly.graph_objs as go
import numpy as np
import time
import os
import plotly.io as pio
import datetime
import pandas as pd
import csv

# Specify the path to your YAML file
yaml_file_path = 'config.yaml'
# Open the YAML file and load its contents
with open(yaml_file_path, 'r') as file:
    config = yaml.safe_load(file)



app = dash.Dash(__name__, external_stylesheets=['/assets/styles.css'], suppress_callback_exceptions=True)


app.layout = html.Div(children = [
    
    html.Div(className='main-div',children=[
        html.Div(className='header-div',children=[
        html.H1("Dashboard",className='title'),
        ]),
        html.Div(className='content-div',children=[
            dcc.Tabs(id="tabs", className="tabs", value='map', children=[
                dcc.Tab(label='Map',className="tab", value='map'),
                dcc.Tab(label='Table',className="tab", value='table'),
                dcc.Tab(label='History',className="tab", value='history')
            ]),
            html.Div(id='tab-content')   
        ]),
    ]),
    
    dcc.Interval(id='interval', interval=30000, n_intervals=0)
])



def get_elevation_map_predicted():
    global config
    with open(yaml_file_path, 'r') as file:
        config = yaml.safe_load(file)
    
    if os.path.exists(config['Data']['elevation_map_predicted_path']):
        return [np.load(config['Data']['elevation_map_predicted_path'], allow_pickle=True),np.load(config['Data']['elevation_map_semi_predicted_path'], allow_pickle=True)]
    else:
        return []
    

def get_volume_mass() :
    global config
    with open(yaml_file_path, 'r') as file:
        config = yaml.safe_load(file)
    
    if os.path.exists(config['MassCalculator']['volume_mass_path']):
        return np.load(config['MassCalculator']['volume_mass_path'], allow_pickle=True)
    else:
        return []
    
def get_densities() :
    global config
    with open(config['MassCalculator']['densities_path'], 'r') as file:
        csv_reader = csv.reader(file)
        try:
            densities = next(csv_reader)
            # Process the densities data
            densities = np.array([float(d) for d in densities])
            return densities
        except StopIteration:
            # Handle the end of iteration
            return []
    
def get_history() :
    global config
    with open(yaml_file_path, 'r') as file:
        config = yaml.safe_load(file)
    
    if os.path.exists(config['watchdog']['historical_data_path']):
        return np.load(config['watchdog']['historical_data_path'], allow_pickle=True)
    else:
        return []
  
 
@app.callback(Output('tab-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'map':
        return html.Div([
            html.Div(className='half',children=[
                html.H3('Graph'),
                dcc.RadioItems(
                    id='graph-selector',
                    options=[
                        {'label': '3D Map', 'value': '3dmap'},
                        {'label': 'Heatmap', 'value': 'heatmap'}
                    ],
                    value='heatmap',
                    labelStyle={'display': 'inline-block'}
                ),
                
                html.Div(id='selected-graph')
            ]),
            html.Div(className='half',children=[
                html.H3('Area info'),
                dcc.Graph(id='mass-graph'),
                #html.Iframe(src="http://10.24.85.31:81/stream" , style={'width':'350px','height':'250px','display' : 'flex'}),
            ])
            
        ])
    elif tab == 'table':
        #read densities
        
        densities = get_densities()
        
        data =dict({       
            'Densities' : ['Densities in T/m3']+[f'{d}' for d in densities],
        })
        df = pd.DataFrame(data, index=[f'{i}' for i in range(11)]).T
        
        return html.Div([
            dash_table.DataTable(
                id='arch_densities_table',
                columns=[{'name': f'', 'id': f'{0}'}]+[{'name': f'Arch {i+1}', 'id': f'{i+1}'} for i in range(10)],
                style_cell={
                    'width': '{}%'.format(1/11*100),
                    'textOverflow': 'ellipsis',
                    'overflow': 'hidden',
                    'textAlign': 'center'
                },
                data= df.to_dict('records'),
                editable=True  # This makes the table cells editable
           ),
            html.Button('Submit', id='submit_densities_button', n_clicks=0),
            dash_table.DataTable(
                id='arch_table',
                columns=[{'name': '', 'id': '0'}]+[{'name': f'Arch {i+1}', 'id': f'{i+1}'} for i in range(10)],
                style_cell={
                    'width': '{}%'.format(1/11*100),
                    'textOverflow': 'ellipsis',
                    'overflow': 'hidden',
                    'textAlign': 'center'
                },
                data=[],
                #editable=True  # This makes the table cells editable
           )
        ])
    
    elif tab == 'history' :
        return html.Div([
            dcc.Graph(id='history-graph')
        ])

            

        

        
        
@app.callback(Output('selected-graph', 'children'),
              Input('graph-selector', 'value'))
def render_graph(selected_graph):
    if selected_graph == '3dmap':
        return dcc.Graph(id='3dmap-graph')
    elif selected_graph == 'heatmap':
        return dcc.Graph(id='heatmap-graph')


@app.callback(Output('heatmap-graph', 'figure'),
              Input('interval', 'n_intervals'))
def update_heatmap(n):
    # Load updated heatmap data from file
    elevation_maps =  get_elevation_map_predicted()
    
    
    
    if len(elevation_maps) :
        elevation_map_predicted=elevation_maps[0]
        elevation_map_semi_predicted=elevation_maps[1]
        
        step = config['Data']['step']
        # Generate heatmap figure
        figure = {
            'data': [
                {'x' : np.arange(0,elevation_map_predicted.shape[1],step), 
                 'y' : np.arange(0,elevation_map_predicted.shape[0],step),
                 'z': elevation_map_predicted.T, 'type': 'heatmap','zmin': -7, 
                'zmax': 15}
            ],
            'layout': {
                'title': 'Heatmap',
                'uirevision' :'true',
                'xaxis': {'title': 'Y Axis', 'aspectmode': 'equal'},
                'yaxis': {'title': 'X Axis', 'scaleanchor': 'x', 'aspectmode': 'equal'},
                
            }
        }
        
        # to do : add a for loop for each observation
        
        # Add vertical line trace to the figure
        observation=config['watchdog']['observations']['gratteur']
        vertical_line_x = float(observation['encoder']['value'])-float(observation['encoder']['y_cord_sensor'])
        vertical_line_trace = go.Scatter(
            x=[vertical_line_x, vertical_line_x],
            y=[0, elevation_map_predicted.shape[1]*step],  # Adjust the y-values range as needed
            mode='lines',
            showlegend=False,
            line=dict(color='rgba(0, 0, 0.5)', width=2),  # Set the color with transparency
            hoverinfo='skip' 
        )
        level_sensor_value = float(config['watchdog']['observations']['gratteur']['level_sensor_1']['value'])
        
        # Add text label near the line
        label_y = elevation_map_predicted.shape[1]*step / 2  # Adjust Y-coordinate of the label
        label_trace = go.Scatter(
            x=[vertical_line_x],
            y=[label_y],
            mode='text',
            text=f'Sensor {int(level_sensor_value)} m',
            textposition='middle right',
            textfont=dict(color='white'),
            showlegend=False,
            hoverinfo='skip'  # Prevent hover information from being displayed for the label
        )

        
        # Add points at the bottom using a scatter trace
        elevation_map_semi_predicted_values = elevation_map_semi_predicted[:, 0]
        observations_trace = go.Scatter(
            x=elevation_map_semi_predicted_values,
            y=np.zeros_like(elevation_map_semi_predicted_values),
            mode='markers',
            marker=dict(color='rgba(0,0,0,0.5)'),
            showlegend=False,
        )
        
        
        
        figure['data'].append(observations_trace)
        figure['data'].append(label_trace)
        figure['data'].append(vertical_line_trace)
        
        return figure
    else :
        return dash.no_update



@app.callback(Output('3dmap-graph', 'figure'),
              Input('interval', 'n_intervals'))
def update_3dmap(n): 
    # Load updated 3dmap data from file
    elevation_map_predicted = get_elevation_map_predicted()[0]
    
    if len(elevation_map_predicted) :
        step = config['Data']['step']
        # Generate 3D surface plot figure
        figure = go.Figure(data=go.Surface(x=np.arange(0,elevation_map_predicted.shape[1],step),y=np.arange(0,elevation_map_predicted.shape[0],step),z=elevation_map_predicted,
                                          cmin=-7,
                                          cmax=15) )

        figure.update_scenes(aspectmode='data')
        figure.update_layout(
            title=f'3D Plot',
            uirevision=True
        )
        return figure
    else :
        return dash.no_update

    
@app.callback(Output('mass-graph', 'figure'),
              Input('interval', 'n_intervals'))
def update_bar_graph(n):
    # Load data for the bar graph
    bar_data = get_volume_mass()[1]
    if len(bar_data) :
        # Generate bar graph figure
        figure = go.Figure(data=go.Bar(x=np.arange(len(bar_data)), y=bar_data))

        figure.update_layout(
            title=f'Mass Arch Graph {int(np.sum(bar_data))} T',
            xaxis=dict(title='Arch'),
            yaxis=dict(title='Mass (T)'),
            uirevision=True
        )
        return figure
    else:
        # Return nothing
        return dash.no_update

    
@app.callback(Output('arch_table', 'data'),
              Input('interval', 'n_intervals'))
def update_arch_table(n):
    
    volume_mass = get_volume_mass()
    
        
    data =dict({
        'Volume' : ['Volume']+[f'{int(v)} m3' for v in volume_mass[0]],
        'Mass' : ['Mass']+[f'{int(m)} T' for m in volume_mass[1]],
        
    })
    df = pd.DataFrame(data, index=[f'{i}' for i in range(11)]).T

    return df.to_dict('records')
        
@app.callback(
    Output('submit_densities_button', 'n_clicks'),
    Input('submit_densities_button', 'n_clicks'),
    State('arch_densities_table', 'data'),
    prevent_initial_call=True
)
def update_densities(n_clicks, arch_densities_data):
    global config
    densities = []
    for i in range(10):
        value = arch_densities_data[0][f'{i+1}']

        # Checking if the value can be converted to a float
        try:
            float_value = float(value)
            densities.append(float_value)
        except ValueError:
            print(f"Value at index {i} is not a valid float: {value}")
            break  # Exit the loop if a non-float value is encountered
    if len(densities) == 10:
        print("write densities")
        with open(config['MassCalculator']['densities_path'], 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(densities)
    
    
@app.callback(
    Output('history-graph', 'figure'),
    Input('interval', 'n_intervals')
)
def update_history(n_intervals):
    history = get_history()

    # Keep only data from the last 10 entries for visualization
    number_of_elements=100
    timestamps = [h['timestamp'] for h in history][:]
    data = [np.sum(h['volume_mass'][1]) for h in history][:]
    
    df = pd.DataFrame({'Timestamp': timestamps, 'Volume Mass': data})
    
    fig = {
        'data': [
            {'x': df['Timestamp'], 'y': df['Volume Mass'], 'type': 'line', 'name': 'Volume Mass'},
        ],
        'layout': {
            'title': f'Historical Volume Mass Data {len(data)} elements',
            'uirevision' :'true',
            'xaxis': {'title': 'Timestamp'},
            'yaxis': {'title': 'Volume Mass'}
        }
    }
    
    return fig


if __name__ == '__main__':
    app.run_server(debug=True,port=8080, host='0.0.0.0')