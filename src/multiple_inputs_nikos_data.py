import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go

import pandas as pd
import pdb

import dash_bootstrap_components as dbc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # [dbc.themes.DARKLY] #

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv('data/nikos-data.csv')

## Create application.
# Table.
# Filters.
# Another table from filters.

features = df.columns

app.layout = html.Div([
    html.Div([
        html.H1('Dash Application', style={'textAlign':'center',
                                'color':'#7FDBFF'}),
        dash_table.DataTable(
            data=df.to_dict('records'),
            sort_action='native',
            columns=[{'name': i, 'id': i} for i in df.columns if i != 'id'],
            style_table={'height':'500px', 'overflowY':'auto'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_cell={
                'minWidth': 95, 'maxWidth': 95, 'width': 95
    }),
    ]),
    html.P(),
    html.H2('Filters'),
    html.Div([
        html.H3('Select column(s)'),
        dcc.Dropdown(id='dropdown',
                     options=[{'label':i, 'value':i} for i in features],
                     value='Data Since',
                     multi=True)],
        style={'width':'25%', 'display':'inline-block'}
    ),
    # checklist filters here
    html.Div([
        html.H3('Select some column(s)'),
        dcc.Checklist(id='checklist',
                     options=[{'label':i, 'value':i} for i in features],
                     value=['Coverage'])],
        style={'width':'98%', 'display':'inline-block'}
    ),
    # two column filters for graphs
    html.H3('Select columns for graph'),
    html.Div([
        dcc.Dropdown(id='xaxis',
                     options=[{'label':i, 'value':i} for i in features],
                     value='Data Since')],
        style={'width':'18%', 'display':'inline-block'}),
    html.Br(),
    html.Div([
        dcc.Dropdown(id='yaxis',
                     options=[{'label':i, 'value':i} for i in features],
                     value='Coverage')],
        style={'width':'18%', 'display':'inline-block'}),
    dcc.Graph(id='feature-graphic'),
    ], style={'padding':10})


@app.callback(Output('feature-graphic', 'figure'),
              [Input('xaxis', 'value'),
               Input('yaxis', 'value')])
def update_graph(xaxis_name, yaxis_name):
    return {'data':[go.Scatter(x=df[xaxis_name],
                               y=df[yaxis_name],
                               text=df['Provider'],
                               mode='markers',
                               marker={'size':15,
                                       'opacity':0.5,
                                       'line':{'width':0.5, 'color':'white'}})
                    ],
            'layout':go.Layout(title='My Dashboard for MPG',
                                xaxis={'title':xaxis_name},
                                yaxis={'title':yaxis_name},
                                hovermode='closest'),}




if __name__ == '__main__':
    app.run_server(debug=True)



# import pdb
# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output
# import plotly.express as px

# import pandas as pd

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')

# available_indicators = df['Indicator Name'].unique()
# pdb.set_trace()

# app.layout = html.Div([
#     html.Div([

#         html.Div([
#             dcc.Dropdown(
#                 id='xaxis-column',
#                 options=[{'label': i, 'value': i} for i in available_indicators],
#                 value='Fertility rate, total (births per woman)'
#             ),
#             dcc.RadioItems(
#                 id='xaxis-type',
#                 options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
#                 value='Linear',
#                 labelStyle={'display': 'inline-block'}
#             )
#         ],
#         style={'width': '48%', 'display': 'inline-block'}),

#         html.Div([
#             dcc.Dropdown(
#                 id='yaxis-column',
#                 options=[{'label': i, 'value': i} for i in available_indicators],
#                 value='Life expectancy at birth, total (years)'
#             ),
#             dcc.RadioItems(
#                 id='yaxis-type',
#                 options=[{'label': i, 'value': i} for i in ['Linear', 'Log']],
#                 value='Linear',
#                 labelStyle={'display': 'inline-block'}
#             )
#         ],style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
#     ]),

#     dcc.Graph(id='indicator-graphic'),

#     dcc.Slider(
#         id='year--slider',
#         min=df['Year'].min(),
#         max=df['Year'].max(),
#         value=df['Year'].max(),
#         marks={str(year): str(year) for year in df['Year'].unique()},
#         step=None
#     )
# ])

# @app.callback(
#     Output('indicator-graphic', 'figure'),
#     Input('xaxis-column', 'value'),
#     Input('yaxis-column', 'value'),
#     Input('xaxis-type', 'value'),
#     Input('yaxis-type', 'value'),
#     Input('year--slider', 'value'))
# def update_graph(xaxis_column_name, yaxis_column_name,
#                  xaxis_type, yaxis_type,
#                  year_value):
#     dff = df[df['Year'] == year_value]

#     fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
#                      y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
#                      hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])

#     fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

#     fig.update_xaxes(title=xaxis_column_name,
#                      type='linear' if xaxis_type == 'Linear' else 'log')

#     fig.update_yaxes(title=yaxis_column_name,
#                      type='linear' if yaxis_type == 'Linear' else 'log')

#     return fig


# if __name__ == '__main__':
#     app.run_server(debug=True)