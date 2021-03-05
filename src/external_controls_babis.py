import random
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash_table import DataTable
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.express as px

import pdb


sample_df = pd.read_csv('data/agro2018/Agro2018_no_nanBABIS.csv', delimiter='\t')
sample_df = sample_df.fillna(0)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([
    html.H1("Εφαρμογή Δεδομένων και Διαγραμμάτων",  style={'textAlign':'center'}),
    html.Hr(),
    html.H2("Επιλέξτε Φίλτρο Δεδομένων"),
    html.Div(dcc.Dropdown(id='countries-radio',
                          options=[{'label': k, 'value': k} for k in sample_df.columns.tolist()],
                          value='Αγροτικά Προϊόντα'),
                                style = {'width': '250px',
                                    'fontSize' : '15px',
                                    'padding-left' : '100px',
                                    'display': 'inline-block'}),
    html.Div(dcc.Dropdown(id='cities-radio'),
             style = {'width': '450px',
                                    'fontSize' : '15px',
                                    'padding-left' : '100px',
                                    'display': 'inline-block'}),
                          
    html.Hr(),

    #html.Div(id='display-selected-values'),
    html.Div(id='display-selected-table',  className='tableDiv'),
    
    html.H2("Διαγράμματα"),
    html.Div(id='datatable-interactivity-container'),
    html.Hr(),
    html.H3('Διαδραστικό Διάγραμμα'),
    html.Div([dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in sample_df.columns.tolist()],
                value='Αγροτικά Προϊόντα'
            ),
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in sample_df.columns.tolist()],
                value='Περιφέρεια (NUTS 2)'
            ),
            ],style={'width': '48%', 'display': 'inline-block'}),
            dcc.Graph(id='indicator-graphic'),
])


@app.callback(
    Output('cities-radio', 'options'),
    Input('countries-radio', 'value'))
def set_cities_options(selected_country):
    return [{'label': i, 'value': i} for i in sample_df[selected_country].unique()]


@app.callback(
    Output('cities-radio', 'value'),
    Input('cities-radio', 'options'))
def set_cities_value(available_options):
    return available_options[0]['value']


# @app.callback(
#     Output('display-selected-values', 'children'),
#     Input('countries-radio', 'value'),
#     Input('cities-radio', 'value'))
# def set_display_children(selected_country, selected_city):
#     return u'{} is a city in {}'.format(
#         selected_city, selected_country,
#     )


@app.callback(
    Output('display-selected-table', 'children'),
    [Input('countries-radio', 'value'),
    Input('cities-radio', 'value')])
def set_display_table(selected_country, selected_city):
    #df_temp = sample_df[sample_df['Αγροτικά Προϊόντα'] == selected_country]
    #df_temp = df_temp[df_temp['Αγροτικά Προϊόντα'] == selected_city]
    df_temp = sample_df[sample_df[selected_country] == selected_city]
    return html.Div([
        dash_table.DataTable(
            id='main-table',
            columns=[{'name': i, 'id': i} for i in df_temp.columns],
             data=df_temp[0:15].to_dict('rows'),
             editable=True,
             filter_action='native',
             sort_action='native',
             sort_mode="multi",
             column_selectable="single",
             row_selectable="multi",
             row_deletable=True,
             selected_columns=[],
             selected_rows=[],
             page_action="native",
             page_current= 0,
             page_size= 10,
             style_table={
                'maxHeight': '50%',
                'overflowY': 'scroll',
                'width': '100%',
                'minWidth': '10%',
            },
            style_header={'backgroundColor': 'rgb(200,200,200)'},
            style_cell={'backgroundColor': 'rgb(230,230,230)','color': 'black','height': 'auto','width': 'auto'},#minWidth': '0px', 'maxWidth': '180px', 'whiteSpace': 'normal'},
            #style_cell={'minWidth': '120px', 'width': '150px', 'maxWidth': '180px'},
              style_data={'whiteSpace': 'auto','height': 'auto','width': 'auto'}
        )
    ])


@app.callback(
    Output('datatable-interactivity-container', "children"),
    Input('countries-radio', 'value'),
    Input('cities-radio', 'value'))
def update_graphs(selected_country, selected_city):
    dff = sample_df[sample_df[selected_country] == selected_city]
    return [
        dcc.Graph(
            id=column,
            figure={
                "data": [
                    {
                        "x": dff['Περιφέρεια (NUTS 2)'].unique(),#dff[selected_country],
                        "y": dff[column],
                        "type": "bar",
                    }
                ],
                "layout": {
                    "xaxis": {"automargin": True},
                    "yaxis": {
                        "automargin": True,
                        "title": {"text": column}
                    },
                    "height": 250,
                    "margin": {"t": 10, "l": 10, "r": 10},
                },
            },
        )
        # check if column exists - user may have deleted it
        # If `column.deletable=False`, then you don't
        # need to do this check.
        for column in ["Ποσότητα Παραγωγής (σε τόνους)", "Κατηγορία Αγροτικών Προϊόντων", "Έκταση (στρέμματα)"] if column in dff
    ]


@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value'),])
def update_graph(xaxis_column_name, yaxis_column_name):
    dff = sample_df

    fig = px.bar(x=dff[xaxis_column_name],
                     y=dff[yaxis_column_name],
                     )

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    fig.update_xaxes(title=xaxis_column_name)

    fig.update_yaxes(title=yaxis_column_name)

    return fig




if __name__ == '__main__':
    app.run_server(debug=True)