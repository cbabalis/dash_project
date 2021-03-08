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
chart_types = ['Γράφημα Στήλης', 'Γράφημα Πίτας']


def get_col_rows_data(selected_country, selected_city, sample_df):
    if selected_country == '':
        df_temp = sample_df
    elif (isinstance(selected_city, str)):
        df_temp = sample_df[sample_df[selected_country] == selected_city]
    else:
        df_temp= sample_df[sample_df[selected_country].isin(selected_city)]
    return df_temp


def get_bar_figure(dff, x_col, y_col, col_sum):
    fig = px.bar(dff, x=x_col, y=y_col, color=col_sum) #x_col)

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    fig.update_xaxes(title=y_col)

    fig.update_yaxes(title=col_sum)
    
    return fig


def get_pie_figure(dff, x_col, col_sum, y_col):
    fig = px.pie(dff, values=col_sum, names=y_col)
    return fig



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
        dcc.Dropdown(id='column-sum',
                          options=[{'label': k, 'value': k} for k in vals_categories],
                          value=''),
    ],style = {'width': '350px',
                                    'fontSize' : '15px',
                                    'padding-left' : '100px',
                                    'display': 'inline-block'}),
    html.Div([html.Label("Επιλογή Γραφήματος"),
        dcc.Dropdown(id='chart-choice',
                          options=[{'label': k, 'value': k} for k in chart_types],
                          value='Γράφημα Στήλης'),
    ],style = {'width': '350px',
                                    'fontSize' : '15px',
                                    'padding-left' : '100px',
                                    'display': 'inline-block'}),
    # table here
    html.Hr(),
    html.Div(id='display-selected-table',  className='tableDiv'),
    
    # graphs here
    html.Hr(),
    dcc.Graph(id='indicator-graphic-multi-sum'),   
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


@app.callback(
    Output('column-sum', 'value'),
    Input('column-sum', 'options'))
def set_sum_values(available_options):
    return available_options[0]['value']


@app.callback(
    Output('chart_choice', 'value'),
    Input('hart_choice', 'options'))
def get_chart_choice(available_options):
    return available_options[0]['value']


@app.callback(
    Output('indicator-graphic-multi-sum', 'figure'),
    [Input('countries-radio', 'value'),
    Input('cities-radio', 'value'),
    Input('products-radio', 'value'),
    Input('products-radio-val', 'value'),
    Input('column-sum', 'value'),
    Input('chart-choice', 'value')])
def set_display_figure(x_col, x_col_vals, y_col, y_col_vals, col_sum, chart_type):
    dff = sample_df[sample_df[x_col].isin(x_col_vals)]
    dff = dff[dff[y_col].isin(y_col_vals)]
    dff = dff.groupby([x_col, y_col])[col_sum].apply(lambda x : x.astype(int).sum())
    dff = dff.reset_index()
    
    if chart_type == 'Γράφημα Στήλης':
        fig = get_bar_figure(dff, x_col, col_sum, y_col)
    elif chart_type == 'Γράφημα Πίτας':
        fig = get_pie_figure(dff, x_col, col_sum, y_col)

    return fig





if __name__ == '__main__':
    app.run_server(debug=True)