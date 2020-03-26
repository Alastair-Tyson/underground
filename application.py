import pandas as pd
import numpy as np
import dash
import pickle
import flask
import math
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import networkx as nx

info=pd.read_csv('stat_cap.csv')

with open('coords.pkl', 'rb') as coords:
    coordinates = pickle.load(coords)
with open('line_list.pkl', 'rb') as line_list:
    line_list = pickle.load(line_list)
with open('stat_list.pkl', 'rb') as stat_list:
    stat_list = pickle.load(stat_list)
with open('G.pkl', 'rb') as G:
    G = pickle.load(G)
with open('col.pkl', 'rb') as col:
    col_list = pickle.load(col)
df_raw = pd.read_csv('./London_Multiplex_Transport/Dataset/london_transport_raw.edges',sep=' ',header=None)
df_raw.columns = ['line','station_1','station_2']
df_nodes = pd.read_csv('./London_Multiplex_Transport/Dataset/london_transport_nodes.txt',sep=' ')

cols={
    'background': '#F0F0F0'
    
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets) 
app.scripts.config.serve_locally = True


app.layout=html.Div(children=[
    html.Div(children=[
        html.H1('Underground Shortest Path Finder',style={'textAlign': 'center'}),
        html.H2('Enter in any two stations to find the shortest path between them',style={'textAlign': 'center'}),
        html.H3('Note: Shortest path in terms of stations, not distance or time',style={'textAlign': 'center'})
    ]),
    html.Div(children=[
        html.H3('Start Station',style={'textAlign': 'center'}),
        dcc.Input(id='start',style={'display': 'inline-block'})
    ],style={'textAlign': 'center'}),
    html.Div(children=[
        html.H3('End Station',style={'textAlign': 'center'}),
        dcc.Input(id='end',style={'display': 'inline-block'})
    ],style={'textAlign': 'center'}),
    html.Div(id='out',children=[
        html.Div(id='length',style={'textAlign': 'center'}),
        html.Div(id='path',style={'textAlign': 'center'}),
        html.Div(id='lines',style={'textAlign': 'center'}),
        dcc.Graph(id='network',style={'backgroundColor': cols['background']})
    ],style={'display':'none'})
    
    
    
],style={'backgroundColor': cols['background']})
@app.callback([Output('out','style'),
               Output('length','children'),
               Output('path','children'),
               Output('lines','children'),
               Output('network','figure')],
             [Input('start','value'),
              Input('end','value')])
def output(start,end):
    start_station=start.lower().replace(' ','')
    end_station=end.lower().replace(' ','')
    try:
        start_node = int(df_nodes.nodeID[df_nodes.nodeLabel == start_station])
    except:
        return[('Your start station does not exist.')], [],[]
    try:
        end_node = int(df_nodes.nodeID[df_nodes.nodeLabel == end_station])
    except:
        return[('Your end station does not exist.')], [],[]
    pathlength = nx.shortest_path_length(G, start_station, end_station)
    path = nx.shortest_path(G, start_station, end_station)
    lines=[]
    for i in range(len(path)):
        try:
            df=df_raw.line[((df_raw.station_1 == path[i]) & (df_raw.station_2 == path[i+1] ))]
            df.reset_index(drop=True,inplace=True)
            if df[0] not in lines:
                lines.append(df[0])
        except:
            try:
                df=df_raw.line[((df_raw.station_1 == path[i+1]) & (df_raw.station_2 == path[i] ))]
                df.reset_index(drop=True,inplace=True)
                if df[0] not in lines:
                    lines.append(df[0])
            except:
                pass
    G_n=nx.Graph()
    for n in path:
        G_n.add_node(stat_list[n])
    colors=[]
    for e in range(len(path)):
        try:
            G_n.add_edge(stat_list[path[e]],stat_list[path[e+1]])
            try:
                line=info.line[((info.station_1 == stat_list[path[e]]) & (info.station_2 == stat_list[path[e+1]] ))].reset_index(drop=True)[0]
                colors.append(col_list[line])
            except:
                line=info.line[((info.station_1 == stat_list[path[e+1]]) & (info.station_2 == stat_list[path[e]] ))].reset_index(drop=True)[0]
                colors.append(col_list[line])

        except:
            pass
    
    edge_x = []
    edge_y = []
    for edge in G_n.edges():
        x0, y0 = coordinates[edge[0]]
        x1, y1 = coordinates[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        hoverinfo='none',
        mode='lines')
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers + text',
        hoverinfo='none',
        textposition='top center')
    
    for node in G_n.nodes():
        x, y = coordinates[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
    node_text = []
    for node,adj in G_n.adjacency():
        node_text.append(node)

    node_trace.marker.color=colors
    edge_trace.marker.color=colors
    node_trace.text = node_text
    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
               
                titlefont_size=16,
                paper_bgcolor=cols['background'],
                showlegend=False,
                height=500,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
            
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
    chil1=[html.H2('Shortest path is ' + str(pathlength) + ' stations')]
    chil2=[html.H2('These stations are: '),
           html.H2([stat_list[stats] +', ' for stats in path])]
    chil3=[html.H2('You will have to take the following lines:'),
           html.H2([line_list[line] +', ' for line in lines])]
    
    
    
    
    return {'display':True},chil1, chil2, chil3,fig

    
application=app.server
if __name__ == '__main__':
    application.run(debug=False)