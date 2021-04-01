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
import urllib
# following two lines for reading filenames from disk
from os import listdir
from os.path import isfile, join
import os


import pdb

my_path = 'matrices_to_show/'
onlyfiles = [f for f in listdir(my_path) if isfile(join(my_path, f))]

matrix_text = '''
#### Ετήσια παραγωγή νωπών και μεταποιημένων αγροτικών προϊόντων και ζωοτροφών σε επίπεδο περιφερειακών ενοτήτων
'''

help_text = '''
ΕΠΕΞΗΓΗΣΕΙΣ ΤΗΣ ΕΦΑΡΜΟΓΗΣ

*Οδηγίες χρήσης:*

- Η εφαρμογή αυτή δίνει την δυνατότητα στον χρήστη να προβάλλει την επιθυμητή πληροφορία από μια μεγάλη βάση δεδομένων.
- Αυτό γίνεται με χρήση φίλτρων.

#### Σειρά επιλογής φίλτρων.
- Πρώτα επιλέγουμε τον πίνακα που μας ενδιαφέρει από το αντίστοιχο φίλτρο επιλογής πίνακα.
- Στη συνέχεια επιλέγουμε την χρονιά που μας ενδιαφέρει.
    * __Περιμένουμε μέχρι να εμφανιστεί η επιλογή!__
- Έπειτα επιλέγουμε τιμές στα υπόλοιπα φίλτρα.
- Περιμένουμε μέχρι να δούμε τις επιλογές μας σε πίνακα.

#### Χρήση διαγραμμάτων
- Με το φίλτρο επιλογής διαγράμματος, επιλέγουμε τύπο διαγράμματος.
- Παρέχονται δύο διαγράμματα:
    - πίτα
    - μπάρες
- Στο τέλος της σελίδας υπάρχει μπάρα επιλογής μήνα για την χρονιά που έχουμε επιλέξει.
    - στην επιλογή 0, προβάλλονται όλα τα στατιστικά για μία χρονιά.
    - σε κάθε άλλη επιλογή, προβάλλεται ο μήνας επιλογής.
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
# doc for image: https://community.plotly.com/t/background-image/21199/5
#image = 'url(http://147.102.154.65/enirisst/images/ampeli-dash.png)'
image = 'url("assets/ampeli-dash.png")'
results_path = '../od-dash/data/prod_cons/'
download_df = []


geospatial_names = ['NUTS2 (κωδικοποίηση NUTS - επίπεδο 2)', 'NUTS3 (κωδικοποίηση NUTS - επίπεδο 3)', 'Όνομα Γεωγραφικής Ενότητας - Επίπεδο Περιφέρειας','Όνομα Γεωγραφικής Ενότητας - Επίπεδο Νομού']
geospatial_categories = ['κωδ. NUTS2', 'κωδ. NUTS3', 'Περιφέρειες (NUTS2)', 'Περ. Ενότητες (NUTS3)']
product_names = ['Μεμονωμένα Αγροτικά Προϊόντα', 'Κατηγορίες Αγροτικών Προϊόντων']
product_categories = ['Αγροτικά Προϊόντα', 'Κατηγορίες Αγροτικών Προϊόντων']
vals_categories = ['Ποσότητα (σε τόνους)', 'Έτος Αναφοράς']
chart_types = ['Γράφημα Στήλης', 'Γράφημα Πίτας']
month_dict = {0: 'Όλοι οι μήνες', 1:'Ιανουάριος', 2:'Φεβρουάριος', 3:'Μάρτιος', 4:'Απρίλιος', 5:'Μάιος', 6:'Ιούνιος', 7:'Ιούλιος', 8:'Αύγουστος', 9:'Σεπτέμβριος', 10:'Οκτώβριος', 11:'Νοέμβριος', 12:'Δεκέμβριος'}


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

    fig.update_xaxes(title=x_col)

    fig.update_yaxes(title=y_col)
    
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
    html.H1("Βάση Δεδομένων Αγροτικών Προϊόντων",  style={'textAlign':'center'}),
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
        html.Div([
            html.Div([
                html.Label("ΔΙΑΘΕΣΙΜΑ ΣΥΝΟΛΑ ΔΕΔΟΜΕΝΩΝ",
                    style={'font-weight': 'bold',
                            'fontSize' : '17px',
                            'margin-left':'auto',
                            'margin-right':'auto',
                            'display':'block'}),
                dcc.Dropdown(id='availability-radio',
                            style={"display": "block",
                    "margin-left": "auto",
                    "margin-right": "auto",
                    # "width":"60%"
                    }), # style solution here: https://stackoverflow.com/questions/51193845/moving-objects-bar-chart-using-dash-python
            ], className='six columns'),
            html.Div([
                html.Label("ΧΡΟΝΙΚΗ ΠΕΡΙΟΔΟΣ",
                        style={'font-weight': 'bold',
                                'fontSize' : '17px'}),
                dcc.Dropdown(id='year-radio'),
            ], className='three columns'),
        ], className='row',
                 style= {'padding-left' : '50px'}), # closes the div for first line (matrix and year)
        html.Hr(),
        html.Div([
            # geospatial filters
            html.Div([
                html.H5("ΓΕΩΓΡΑΦΙΚΗ ΕΝΟΤΗΤΑ"),
                html.Label("ΚΩΔΙΚΟΠΟΙΗΣΗ - ΕΠΙΠΕΔΟ ΑΝΑΛΥΣΗΣ",
                        style={'font-weight': 'bold',
                                'fontSize' : '17px'}),
                dcc.Dropdown(id='countries-radio',
                                options=[{'label': l, 'value': k} for l, k in zip(geospatial_names, geospatial_categories)],
                                value=''),
                html.Label("ΠΕΡΙΟΧΕΣ",
                        style={'font-weight': 'bold',
                                'fontSize' : '17px'}),
                dcc.Dropdown(id='cities-radio', multi=True),],
                                        style = {'width': '440px',
                                            'fontSize' : '15px',
                                            'padding-left' : '50px',
                                            'display': 'inline-block',
                                            }),
            # product filters
            html.Div([
                html.H5("ΑΓΡΟΤΙΚΑ ΠΡΟΪΟΝΤΑ"),
                html.Label("ΚΑΤΗΓΟΡΙΕΣ",
                        style={'font-weight': 'bold',
                                'fontSize' : '17px'}),
                dcc.Dropdown(id='products-radio',
                                options=[{'label': l, 'value': k} for l, k in zip(product_names, product_categories)],
                                value=''),
                html.Label("ΠΡΟΪΟΝ",
                        style={'font-weight': 'bold',
                                'fontSize' : '17px'}),
                dcc.Dropdown(id='products-radio-val', multi=True),],
                                        style = {'width': '440px',
                                            'fontSize' : '15px',
                                            'padding-left' : '50px',
                                            'display': 'inline-block'}),
            
            # values filters
            html.Div([
                html.Label("ΣΤΑΤΙΣΤΙΚΑ ΣΤΟΙΧΕΙΑ",
                        style={'font-weight': 'bold',
                                'fontSize' : '17px'}),
                dcc.Dropdown(id='column-sum',
                                options=[{'label': k, 'value': k} for k in vals_categories],
                                value=''),
                html.Label("ΕΠΙΛΟΓΗ ΓΡΑΦΗΜΑΤΟΣ",
                        style={'font-weight': 'bold',
                                'fontSize' : '17px'}),
                dcc.RadioItems(id='chart-choice',
                                options=[{'label': k, 'value': k} for k in chart_types],
                                value='Γράφημα Στήλης',
                                labelStyle={'display': 'inline-block', 'text-align': 'justify'}),
            ],style = {'width': '350px',
                                            'fontSize' : '15px',
                                            'padding-left' : '50px',
                                            'display': 'inline-block'}),
        ],className='row'),
    ],style = {'background-image':image,
                                    'background-size':'cover',
                                    'background-position':'right'}),
    # table here
    html.Hr(),
    html.Div(id='display-selected-table',  className='tableDiv'),
    html.Hr(),
    html.Div([
    html.H5("Επιλογή Περιόδου"),
    dcc.Slider(id='slider',
                    min=0,
                    max=12,
                    step=1,
                    marks= month_dict,#{i: str(i) for i in range(0, 12)},
                    value=0),
    html.Div(id='output-container-slider'),
    ],  style={'backgroundColor':'#CEFFBD',
               'font-weight': 'bold',
               'fontSize' : '17px',
               'color':'#111111'}),
    
    # graphs here
    html.Hr(),
    dcc.Graph(id='indicator-graphic-multi-sum'),
    html.Button('Αποθήκευση Παραμέτρων', id='csv_to_disk', n_clicks=0),
    html.Div(id='download-link'),
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
    Input('year-radio', 'value'),
    Input('slider', 'value')
    ])
def set_display_table(selected_country, selected_city, selected_prod_cat, selected_prod_val, selected_matrix, year_val, month_val):
    dff = get_col_rows_data(selected_country, selected_city, sample_df)
    if (year_val):
        dff = dff[dff[REPORT_YEAR] == year_val]
    if (month_val):
        dff = dff[dff[MONTH] == month_val]
    elif month_val == 0:
        dff = dff
    df_temp = get_col_rows_data(selected_prod_cat, selected_prod_val, dff)
    global download_df
    download_df = df_temp # remove this if it is not necessary
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
            #  page_action="native",
            #  page_current= 0,
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
    dff = dff.groupby([x_col, y_col, MONTH])[col_sum].apply(lambda x : x.astype(float).sum())
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
        return "Αποτελέσματα για όλους τους μήνες."
    #return "Στοιχεία για τον {}o μήνα".format(value)
    return "Τα στοιχεία αφορούν τον μήνα: {}".format(month_dict[value])


@app.callback(Output('download-link', 'href'),
              Input('csv_to_disk', 'n_clicks'),)
def save_df_conf_to_disk(btn_click):
    fpath = results_path + 'temp_results.csv'
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'csv_to_disk' in changed_id:
        download_df.to_csv(fpath, sep='\t')
        msg = 'Οι παράμετροι αποθηκεύθηκαν.'
    else:
        msg = 'Δεν επιλέχθηκαν όλες οι παράμετροι.'
    return msg


if __name__ == '__main__':
    app.run_server(debug=True, port=8054)