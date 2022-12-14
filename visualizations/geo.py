import os

import pandas as pd
import plotly.graph_objects as go

import utils.data


def create_map(data: pd.DataFrame) -> go.Figure:
    """
    Function that creates a GeoViz given a DataFrame
    :param data: A Pandas DataFrame that represents the data to visualize!
    :param id: Optional object id for the dcc.Graph object
    :return: dcc.Graph object
    """

    fig = go.Figure()

    scatter_trace = go.Scattermapbox(lat=data["latitude"],
                                     lon=data["longitude"])

    fig.add_trace(scatter_trace)

    fig.update_layout(mapbox_style=os.environ['MAPBOX_STYLE'],
                      mapbox_accesstoken=os.environ['MAPBOX_TOKEN'])
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_layout(height=650)
    fig['layout']['uirevision'] = 'userpref'

    return fig


def update_map(fig: go.Figure, data: pd.DataFrame):
    for d in fig.data:
        d.visible = False

    fig.update_layout(showlegend=False)
    # print(f"Number of traces: {len(fig.data)}")
    scatter_trace = go.Scattermapbox(lat=data["latitude"],
                                     lon=data["longitude"],
                                     marker={'color': data['shaded_color']},
                                     customdata=utils.data.get_custom_data(data),
                                     hovertemplate='<b>Lat: </b>%{lat}<br>'
                                                   '<b>Lon: </b>%{lon}<br><br>'
                                                   '<b>Name: </b>%{customdata[0]}<br><br>'
                                                   '<b>Year: </b>%{customdata[4]}<br><br>'
                                                   '<b>Location Description </b><br>%{customdata[1]}<br><br>'''
                                                   '<b>Attack Description </b><br>%{customdata[2]}<br>')

    fig.add_trace(scatter_trace)
    fig['layout']['uirevision'] = 'userpref'


map = create_map(utils.data.pirate_attacks)
