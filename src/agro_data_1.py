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

geospatial_categories = ['Κωδικοποίηση NUTS 2', 'Περιφέρεια (NUTS 2)', 'Κωδικοποίηση NUTS 3', 'Περιφερειακή Ενότητα (NUTS 3)']
product_categories = ['Αγροτικά Προϊόντα', 'Κατηγορία Αγροτικών Προϊόντων', 'Κατηγοριοποίηση Αγροτικών Προϊόντων ανάλογα με την χρήση']
vals_categories = ['Έκταση (στρέμματα)', 'Ποσότητα Παραγωγής (σε τόνους)', 'Αριθμός Δέντρων	Έτος Αναφοράς']


def get_col_rows_data(selected_country, selected_city, sample_df):
    if selected_country == '':
        df_temp = sample_df
    elif (isinstance(selected_city, str)):
        df_temp = sample_df[sample_df[selected_country] == selected_city]
    else:
        df_temp= sample_df[sample_df[selected_country].isin(selected_city)]
    return df_temp



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1("Δεδομένα και Διαγράμματα",  style={'textAlign':'center'}),
    html.Hr(),
    # filters here
    html.H3("Επιλογή Μεταβλητών"),
    # geospatial filters
    html.Div([
        html.Label("Επιλέξτε Εδαφικές Μονάδες"),
        dcc.Dropdown(id='countries-radio',
                          options=[{'label': k, 'value': k} for k in geospatial_categories],
                          value=''),
        html.Label("Επιλέξτε Περιοχές"),
        dcc.Dropdown(id='cities-radio', multi=True),],
                                style = {'width': '350px',
                                    'fontSize' : '15px',
                                    'padding-left' : '100px',
                                    'display': 'inline-block'}),
    # product filters
    html.Div([html.Label("Επιλέξτε Κατηγορίες ή αγροτικά προϊόντα"),
        dcc.Dropdown(id='products-radio',
                          options=[{'label': k, 'value': k} for k in product_categories],
                          value=''),
        html.Label("Επιλέξτε Τιμές"),
        dcc.Dropdown(id='products-radio-val', multi=True),],
                                style = {'width': '350px',
                                    'fontSize' : '15px',
                                    'padding-left' : '100px',
                                    'display': 'inline-block'}),
    
    # values filters
    html.Div([html.Label("Επιλέξτε Τιμή Προβολής"),
        dcc.Dropdown(id='val-radio',
                          options=[{'label': k, 'value': k} for k in vals_categories],
                          value=''),
    ],style = {'width': '350px',
                                    'fontSize' : '15px',
                                    'padding-left' : '100px',
                                    'display': 'inline-block'}),
    # table here
    html.Hr(),
    html.Div(id='display-selected-table',  className='tableDiv'),

    
    # graphs here
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

@app.callback(
    Output('products-radio-val', 'options'),
    Input('products-radio', 'value'))
def set_products_options(selected_country):
    return [{'label': i, 'value': i} for i in sample_df[selected_country].unique()]


@app.callback(
    Output('products-radio-val', 'value'),
    Input('products-radio-val', 'options'))
def set_products_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('display-selected-table', 'children'),
    [Input('countries-radio', 'value'),
    Input('cities-radio', 'value'),
    Input('products-radio', 'value'),
    Input('products-radio-val', 'value'),
    ])
def set_display_table(selected_country, selected_city, selected_prod_cat, selected_prod_val):
    dff = get_col_rows_data(selected_country, selected_city, sample_df)
    df_temp = get_col_rows_data(selected_prod_cat, selected_prod_val, dff)
    return html.Div([
        dash_table.DataTable(
            id='main-table',
            columns=[{'name': i, 'id': i} for i in df_temp.columns],
             data=df_temp.to_dict('rows'),
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



if __name__ == '__main__':
    app.run_server(debug=True)