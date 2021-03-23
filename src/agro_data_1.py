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
# following two lines for reading filenames from disk
from os import listdir
from os.path import isfile, join


import pdb

my_path = 'matrices_to_show/'
onlyfiles = [f for f in listdir(my_path) if isfile(join(my_path, f))]

matrix_text = '''
### Πίνακας Προϊόντων ανά Περιφέρεια της Ελλάδας.
*Σύντομη περιγραφή*: Επιλογή με βάση τον κωδικό Νuts 2.
'''

help_text = '''
ΕΠΕΞΗΓΗΣΕΙΣ ΤΗΣ ΕΦΑΡΜΟΓΗΣ

Οδηγίες χρήσης:
- Πρώτα επιλέγουμε από το φίλτρο επιλογής πίνακα.
- Έπειτα επιλέγουμε τιμές στα υπόλοιπα φίλτρα.
- Περιμένουμε λίγο.
'''


def convert_weeks_to_units(df):
    # convert to date
    df['week'] = df['Έτος αναφοράς'].astype(str) + df['Εβδομάδα'].astype(str)
    df['week'] = df['week'].str.replace(r'w', '')
    df['week'] = df['week'].astype(int)
    df['LastDayWeek'] = pd.to_datetime((df['week']-1).astype(str) + "6", format="%Y%U%w")
    # convert to months, quarters in new columns
    df[MONTH] = pd.DatetimeIndex(df['LastDayWeek']).month
    df['Τετράμηνο'] = pd.DatetimeIndex(df['LastDayWeek']).quarter
    # return dataframe
    return df


def refine_df(df):
    df = df.fillna(0)
    df = convert_weeks_to_units(df)
    return df


def load_matrix(selected_matrix):
    matrix_filepath = my_path + selected_matrix
    sample_df = pd.read_csv(matrix_filepath, delimiter='\t')
    sample_df = refine_df(sample_df)
    return sample_df


sample_df = []
# sample_df = pd.read_csv('data/Table_qikw_BABIS.csv', delimiter='\t')
# sample_df = sample_df.fillna(0)
# sample_df = convert_weeks_to_units(sample_df)
PROD_AVAILABILITY = 'Διάθεση Αγροτικών Προϊόντων'
REPORT_YEAR = 'Έτος αναφοράς'
MONTH = 'Μήνας'
image = 'url(https://upload.wikimedia.org/wikipedia/commons/0/06/Location_map_of_WesternGreece_%28Greece%29.svg)'


geospatial_names = ['Επιλογή με βάση τον κωδικό NUTS2 της περιφέρειας', 'Επιλογή με βάση το όνομα της Περιφέρειας (NUTS2)','Επιλογή με βάση τον κωδικό NUTS3 του Νομού','Επιλογή με βάση το όνομα του Νομού (NUTS3)']
geospatial_categories = ['κωδ. NUTS2', 'Περιφέρειες (NUTS2)', 'κωδ. NUTS3', 'Περ. Ενότητες (NUTS3)']
product_categories = ['Αγροτικά Προϊόντα', 'Κατηγορίες Αγροτικών Προϊόντων']
#vals_categories = ['Εκτάσεις (σε στρέμματα)', 'Παραγωγή (σε τόνους)', 'Πλήθος Δέντρων', 'Έτος Αναφοράς']
vals_categories = ['Παραγωγή (σε τόνους)', 'Έτος Αναφοράς']
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
    fig = px.bar(dff, x=x_col, y=y_col, color=col_sum)

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest',
        #title= u'Διάγραμμα μεταβλητών {} και {}'.format(x_col,y_col),
        font=dict(
        family="Courier New, monospace",
        size=15,
        color="RebeccaPurple"
    ))
    
    fig.update_traces( textposition='auto')

    fig.update_xaxes(title=y_col)

    fig.update_yaxes(title=col_sum)
    
    return fig


def get_pie_figure(dff, x_col, col_sum, y_col):
    fig = px.pie(dff, values=col_sum, names=y_col)
    fig.update_traces(textposition='inside', textinfo='percent', hoverinfo='label+value', textfont_size=20)
    fig.update_layout(uniformtext_minsize=20, uniformtext_mode='hide',
        font=dict(
        family="Courier New, monospace",
        size=15,
        color="RebeccaPurple"
    ))
    return fig



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1("Δεδομένα και Διαγράμματα",  style={'textAlign':'center'}),
    html.Hr(),
    # text here
    html.Div([
    dcc.Markdown(matrix_text),
    dcc.ConfirmDialogProvider(children=html.Button(
            'Οδηγίες Χρήσης',
            style={'float': 'right','margin': 'auto'}
        ),
        id='danger-danger-provider',
        message=help_text,
    ),
    html.Div(id='output-provider')
    ],
             className='row'),
    # filters here
    html.Div([
    html.H3("Επιλογή Μεταβλητών"),
    # geospatial filters
    html.Div([
        html.Label("Επιλέξτε έτος προβολής",
                   style={'font-weight': 'bold',
                          'fontSize' : '17px'}),
        dcc.Dropdown(id='year-radio'),
        html.Label("Επιλέξτε Εδαφικές Μονάδες",
                   style={'font-weight': 'bold',
                          'fontSize' : '17px'}),
        dcc.Dropdown(id='countries-radio',
                          options=[{'label': l, 'value': k} for l, k in zip(geospatial_names, geospatial_categories)],
                          value=''),
        html.Label("Επιλέξτε Περιοχές",
                   style={'font-weight': 'bold',
                          'fontSize' : '17px'}),
        dcc.Dropdown(id='cities-radio', multi=True),],
                                style = {'width': '400px',
                                    'fontSize' : '15px',
                                    'padding-left' : '50px',
                                    'display': 'inline-block'}),
    # product filters
    html.Div([
        html.Label("Επιλέξτε πίνακα προς προβολή",
                   style={'font-weight': 'bold',
                          'fontSize' : '17px'}),
        dcc.Dropdown(id='availability-radio'),
        html.Label("Επιλέξτε Αγροτικά Προϊόντα",
                   style={'font-weight': 'bold',
                          'fontSize' : '17px'}),
        dcc.Dropdown(id='products-radio',
                          options=[{'label': k, 'value': k} for k in product_categories],
                          value=''),
        html.Label("Επιλέξτε Τιμές",
                   style={'font-weight': 'bold',
                          'fontSize' : '17px'}),
        dcc.Dropdown(id='products-radio-val', multi=True),],
                                style = {'width': '350px',
                                    'fontSize' : '15px',
                                    'padding-left' : '50px',
                                    'display': 'inline-block'}),
    
    # values filters
    html.Div([
        html.Label("Επιλέξτε Τιμή Προβολής (για διάγραμμα)",
                   style={'font-weight': 'bold',
                          'fontSize' : '17px'}),
        dcc.Dropdown(id='column-sum',
                          options=[{'label': k, 'value': k} for k in vals_categories],
                          value=''),
    ],style = {'width': '350px',
                                    'fontSize' : '15px',
                                    'padding-left' : '50px',
                                    'display': 'inline-block'}),
    html.Div([html.Label("Επιλογή Γραφήματος",
                   style={'font-weight': 'bold',
                          'fontSize' : '17px'}),
        dcc.Dropdown(id='chart-choice',
                          options=[{'label': k, 'value': k} for k in chart_types],
                          value='Γράφημα Στήλης'),
    ],style = {'width': '350px',
                                    'fontSize' : '15px',
                                    'padding-left' : '50px',
                                    'display': 'inline-block'}),
    ],
                      style = {'background-image':image,
                                    'background-size':'cover',
                                    'background-position':'right'}),
    # table here
    html.Hr(),
    html.Div(id='display-selected-table',  className='tableDiv'),
    
    # graphs here
    html.Hr(),
    dcc.Graph(id='indicator-graphic-multi-sum'),
    dcc.Slider(id='slider',
                    min=1,
                    max=12,
                    step=1,
                    marks={i: str(i) for i in range(0, 12)},
                    value=0),
    html.Div(id='output-container-slider')
])


@app.callback(
    Output('cities-radio', 'options'),
    [Input('availability-radio', 'value'),
    Input('countries-radio', 'value')])
def set_cities_options(selected_matrix, selected_country):
    #sample_df = load_matrix(selected_matrix)
    return [{'label': i, 'value': i} for i in sample_df[selected_country].unique()]


@app.callback(
    Output('cities-radio', 'value'),
    Input('cities-radio', 'options'))
def set_cities_value(available_options):
    return available_options[0]['value']

@app.callback(
    Output('products-radio-val', 'options'),
    [Input('availability-radio', 'value'),
    Input('products-radio', 'value')])
def set_products_options(selected_matrix, selected_country):
    #sample_df = load_matrix(selected_matrix)
    return [{'label': i, 'value': i} for i in sample_df[selected_country].unique()]


@app.callback(
    Output('products-radio-val', 'value'),
    Input('products-radio-val', 'options'))
def set_products_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('availability-radio', 'options'),
    Input('availability-radio', 'value'))
def set_products_options(selected_country):
    #return [{'label': i, 'value': i} for i in sample_df[PROD_AVAILABILITY].unique()]
    return [{'label': i, 'value': i} for i in onlyfiles]


@app.callback(
    Output('year-radio', 'options'),
    [Input('availability-radio', 'value'),
    Input('year-radio', 'value')])
def set_products_options(selected_matrix, selected_country):
    global sample_df
    sample_df = load_matrix(selected_matrix)
    return [{'label': i, 'value': i} for i in sample_df[REPORT_YEAR].unique()]



@app.callback(
    Output('display-selected-table', 'children'),
    [Input('countries-radio', 'value'),
    Input('cities-radio', 'value'),
    Input('products-radio', 'value'),
    Input('products-radio-val', 'value'),
    Input('availability-radio', 'value'),
    Input('year-radio', 'value')
    ])
def set_display_table(selected_country, selected_city, selected_prod_cat, selected_prod_val, selected_matrix, year_val):
    dff = get_col_rows_data(selected_country, selected_city, sample_df)
    if (year_val):
        dff = dff[dff[REPORT_YEAR] == year_val]
    df_temp = get_col_rows_data(selected_prod_cat, selected_prod_val, dff)
    return html.Div([
        dash_table.DataTable(
            id='main-table',
            columns=[{'name': i, 'id': i, 'hideable':True} for i in df_temp.columns],
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
             hidden_columns=['LastDayWeek', 'week'],
             page_action="native",
             page_current= 0,
             page_size= 10,
             style_table={
                'maxHeight': '50%',
                'overflowY': 'scroll',
                'width': '100%',
                'minWidth': '10%',
            },
            style_header={'backgroundColor': 'rgb(200,200,200)', 'width':'auto'},
            style_cell={'backgroundColor': 'rgb(230,230,230)','color': 'black','height': 'auto','minWidth': '100px', 'width': '150px', 'maxWidth': '180px','overflow': 'hidden', 'textOverflow': 'ellipsis', },#minWidth': '0px', 'maxWidth': '180px', 'whiteSpace': 'normal'},
            #style_cell={'minWidth': '120px', 'width': '150px', 'maxWidth': '180px'},
            style_data={'whiteSpace': 'auto','height': 'auto','width': 'auto'},
            tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in df_temp.to_dict('records')
            ],
            tooltip_header={i: i for i in df_temp.columns},
    tooltip_duration=None
        )
    ])


@app.callback(
    Output('column-sum', 'value'),
    Input('column-sum', 'options'))
def set_sum_values(available_options):
    return available_options[0]['value']


@app.callback(
    Output('chart_choice', 'value'),
    Input('chart_choice', 'options'))
def get_chart_choice(available_options):
    return available_options[0]['value']


@app.callback(
    Output('indicator-graphic-multi-sum', 'figure'),
    [Input('countries-radio', 'value'),
    Input('cities-radio', 'value'),
    Input('products-radio', 'value'),
    Input('products-radio-val', 'value'),
    Input('column-sum', 'value'),
    Input('chart-choice', 'value'),
    Input('availability-radio', 'value'),
    Input('year-radio', 'value'),
    Input('slider', 'value')
    ])
def set_display_figure(x_col, x_col_vals, y_col, y_col_vals, col_sum, chart_type, selected_matrix, year_val, month_val):
    #sample_df = load_matrix(selected_matrix)
    dff = sample_df[sample_df[x_col].isin(x_col_vals)]
    dff = dff[dff[y_col].isin(y_col_vals)]
    if (year_val):
        dff = dff[dff[REPORT_YEAR] == year_val]
    if (month_val):
        dff = dff[dff[MONTH] == month_val]
    elif month_val == 0:
        dff = dff
    dff = dff.groupby([x_col, y_col, MONTH])[col_sum].apply(lambda x : x.astype(int).sum())
    dff = dff.reset_index()
    
    if chart_type == 'Γράφημα Στήλης':
        fig = get_bar_figure(dff, x_col, col_sum, y_col)
    elif chart_type == 'Γράφημα Πίτας':
        fig = get_pie_figure(dff, x_col, col_sum, y_col)

    return fig


@app.callback(Output('output-provider', 'children'),
              Input('danger-danger-provider', 'submit_n_clicks'))
def update_output(submit_n_clicks):
    """ documentation: https://dash.plotly.com/dash-core-components/confirmdialogprovider"""
    if not submit_n_clicks:
        return ''
    return """
        Ευχαριστούμε που χρησιμοποιήσατε τις οδηγίες.
    """


@app.callback(
    Output('output-container-slider', 'children'),
    [Input('slider', 'value')]
)
def update_slider(value):
    if value == 0:
        return "Βλέπετε τα αποτελέσματα για όλους τους μήνες."
    return "Επιλέξατε τον '{}' μήνα".format(value)


if __name__ == '__main__':
    app.run_server(debug=True)