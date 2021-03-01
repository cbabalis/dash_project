""" module to simulate eurostat functionality on data. """


# import dash
# import dash_table
# import dash_core_components as dcc
# import dash_html_components as html
# import pandas as pd
# import dash_core_components as dcc
# import dash_html_components as html
# from dash.dependencies import Input, Output
# import plotly.express as px
# import plotly.graph_objs as go

# import pdb


# # read data
# df = pd.read_csv('data/Agro2018_no_nan.csv', delimiter='\t')
# features = df.columns

# app = dash.Dash(__name__)

# app.layout = html.Div([
#     html.H1('Εφαρμογή Προβολής και Επεξεργασίας Δεδομένων', style={'textAlign':'center',
#                                 'color':'#7FDBFF'}),
#     html.H2('Φίλτρα για τον πίνακα'),
#     html.Div([
#         html.H3('Επιλογή στηλών ενδιαφέροντος'),
#         dcc.Dropdown(id='dropdown',
#                      options=[{'label':i, 'value':i} for i in features],
#                      value='Product,Category',
#                      multi=True)],
#         style={'width':'50%', 'display':'inline-block'}
#     ),
#     html.Br(),
    
#     html.H3('Τιμές για τα επιλεγμένα φίλτρα'),
#     html.Br(),
    
#     html.H2('Πίνακας Δεδομένων'),
#     html.Br(),
    
#     html.H2('Διαγράμματα'),
#     html.Br(),
#     html.H2('Πίτες')
# ])


import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table as dt
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd

df = pd.read_csv('data/Agro2018_no_nan.csv', delimiter='\t')

app = dash.Dash(__name__)
#style={'visibility': 'hidden'}

dpdown = []
for i in df['NUTS_3'].unique() :
   str(dpdown.append({'label':i,'value':(i)}))

app.layout = html.Div([
             html.P([
             html.Label("Choose a feature"),
             html.Div(dcc.Dropdown(id='dropdown', options=dpdown),
                                style = {'width': '250px',
                                    'fontSize' : '15px',
                                    'padding-left' : '100px',
                                    'display': 'inline-block'})]),


    #style={'visibility': 'hidden'},
            html.Div(id='table-container',  className='tableDiv'),
            dcc.Graph(id = 'plot',style={'height' : '25%', 'width' : '25%'})

   ])
    #dcc.Dropdown(id='dropdown', style={'height': '30px', 'width': '100px'}, options=dpdown),
    #dcc.Graph(id='graph'),
                #html.Div(html.H3('country graph'),id='table-container1',className='tableDiv1')





@app.callback(
    dash.dependencies.Output('table-container','children'),
    [dash.dependencies.Input('dropdown', 'value')])

def display_table(dpdown):
    df_temp = df[df['NUTS_3']==dpdown]
    return html.Div([
        dt.DataTable(
            id='main-table',
            columns=[{'name': i, 'id': i} for i in df_temp.columns],
             data=df_temp[0:5].to_dict('rows'),
             style_table={
                'maxHeight': '20%',
                #'overflowY': 'scroll',
                'width': '30%',
                'minWidth': '10%',
            },
            style_header={'backgroundColor': 'rgb(200,200,200)'},
            style_cell={'backgroundColor': 'rgb(230,230,230)','color': 'black','height': 'auto','width': 'auto'},#minWidth': '0px', 'maxWidth': '180px', 'whiteSpace': 'normal'},
            #style_cell={'minWidth': '120px', 'width': '150px', 'maxWidth': '180px'},
              style_data={'whiteSpace': 'auto','height': 'auto','width': 'auto'}

    )

    ])



if __name__ == '__main__':
    app.run_server(debug=True)
