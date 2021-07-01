import random
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_table import DataTable
from dash.exceptions import PreventUpdate
import pandas as pd
import geopandas as gpd
import plotly.express as px
import urllib
# following two lines for reading filenames from disk
from os import listdir
from os.path import isfile, join
from datetime import datetime
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
import os
import plotly.graph_objects as go
import time



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

Τα βήματα που ακολουθούνται είναι τα εξής:

1. Ο χρήστης επιλέγει σύνολο δεδομένων από τα ΔΙΑΘΕΣΙΜΑ ΣΥΝΟΛΑ ΔΕΔΟΜΕΝΩΝ.
2. Όταν το επιλεγμένο σύνολο δεδομένων φορτωθεί, τότε το φίλτρο με τίτλο ΧΡΟΝΙΚΗ ΠΕΡΙΟΔΟΣ γίνεται διαθέσιμο.
3. Στη συνέχεια ο χρήστης επιλέγει από τα φίλτρα ΚΩΔΙΚΟΠΟΙΗΣΗ-ΕΠΙΠΕΔΟ ΑΝΑΛΥΣΗΣ και ΚΑΤΗΓΟΡΙΕΣ.
4. Έπειτα επιλέγει ΠΕΡΙΟΧΕΣ και ΠΡΟΪΟΝ αντίστοιχα.

Είναι σημαντικό να τηρηθεί η σειρά για την εύρυθμη λειτουργία της εφαρμογής.

Επιπλέον παρέχονται φίλτρα για την τιμή προβολής αλλά και το είδος του γραφήματος που επιθυμεί ο χρήστης.
- Με το φίλτρο επιλογής διαγράμματος, επιλέγουμε τύπο διαγράμματος.
- Παρέχονται δύο διαγράμματα:
    - πίτα
    - μπάρες

Το κουμπί ΑΠΟΘΗΚΕΥΣΗ ΠΑΡΑΜΕΤΡΩΝ σώζει τον πίνακα κατόπιν της εφαρμογής των φίλτρων στον δίσκο (δεν είναι διαθέσιμη η λειτουργικότητα για όλους τους χρήστες).
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


def _create_results_name():
    now = datetime.now()
    created_on = now.strftime(("%Y-%m-%d-%H-%M-%S"))
    results_name = 'custom_file_' + str(created_on) + '.csv'
    return results_name


sample_df = []
# sample_df = pd.read_csv('data/Table_qikw_BABIS.csv', delimiter='\t')
# sample_df = sample_df.fillna(0)
# sample_df = convert_weeks_to_units(sample_df)
PROD_AVAILABILITY = 'Διάθεση Αγροτικών Προϊόντων'
REPORT_YEAR = 'Έτος αναφοράς'
MONTH = 'Μήνας'
REGIONAL_UNITS = 'Περ. Ενότητες (NUTS3)'
# doc for image: https://community.plotly.com/t/background-image/21199/5
#image = 'url(http://147.102.154.65/enirisst/images/ampeli-dash.png)'
image = 'url("assets/ampeli-dash.png")'
results_path = '../od-dash/data/prod_cons/'
download_df = []

# TODO selection that is the same as the download_df, but for consumptions.
# It has to be a variable later
download_cons_df = []


geospatial_names = ['NUTS2 (κωδικοποίηση NUTS - επίπεδο 2)', 'NUTS3 (κωδικοποίηση NUTS - επίπεδο 3)', 'Όνομα Γεωγραφικής Ενότητας - Επίπεδο Περιφέρειας','Όνομα Γεωγραφικής Ενότητας - Επίπεδο Νομού']
geospatial_categories = ['κωδ. NUTS2', 'κωδ. NUTS3', 'Περιφέρειες (NUTS2)', 'Περ. Ενότητες (NUTS3)']
product_names = ['Μεμονωμένα Αγροτικά Προϊόντα', 'Κατηγορίες Αγροτικών Προϊόντων']
product_categories = ['Αγροτικά Προϊόντα', 'Κατηγορίες Αγροτικών Προϊόντων']
vals_categories = ['Ποσότητα (σε τόνους)', 'Έτος Αναφοράς']
chart_types = ['Γράφημα Στήλης', 'Γράφημα Πίτας', 'Choropleth']
month_dict = {0: 'Όλοι οι μήνες', 1:'Ιανουάριος', 2:'Φεβρουάριος', 3:'Μάρτιος', 4:'Απρίλιος', 5:'Μάιος', 6:'Ιούνιος', 7:'Ιούλιος', 8:'Αύγουστος', 9:'Σεπτέμβριος', 10:'Οκτώβριος', 11:'Νοέμβριος', 12:'Δεκέμβριος'}

colorscales = px.colors.named_colorscales()
basemaps = ["white-bg", "open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner", "stamen-watercolor"]

white_button_style = {'background-color': 'white',
                      'color': 'black',
                      #'height': '50px',
                      #'width': '100px',
                      'margin-top': '50px',
                      'margin-left': '50px'}


def get_col_rows_data(selected_country, selected_city, sample_df):
    if selected_country == '':
        df_temp = sample_df
    elif (isinstance(selected_city, str)):
        df_temp = sample_df[sample_df[selected_country] == selected_city]
    else:
        df_temp = sample_df[sample_df[selected_country].isin(selected_city)]
    return df_temp


def _get_corresponding_cons_df(selected_country, selected_city):
    if selected_country == '':
        df_temp = load_matrix('Εβδομαδιαία_Ζήτηση_Νωπών_babis.csv')
    elif (isinstance(selected_city, str)):
        df_temp = sample_df[sample_df[selected_country] == selected_city]
    else:
        df_temp = sample_df[sample_df[selected_country].isin(selected_city)]
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


def get_choropleth_figure(dff, x_col, col_sum, colorscale, basemap, regions='', stats_to_show=''):
    """Method to show a choropleth map with data.

    Args:
        dff (Dataframe): Data to be seen in map.
        regions (dataframe, optional): dataframe of regions and geometry. Defaults to ''.
        stats_to_show (str, optional): column with data. Defaults to ''.
    """
    # if regions is empty, get regions from disk.
    start_time = time.time()
    regions_df = _get_regions(regions, names_col='Regional_U')
    print("regions df ended in --- %s seconds ---" % (time.time() - start_time))
    # join regions with incoming data.
    start_time = time.time()
    gdf = _join_data_with_regions(regions_df, dff, col_sum, 'Regional_U')
    print("join data with regions ended in --- %s seconds ---" % (time.time() - start_time))
    # show everything on map.
    start_time = time.time()
    fig = _create_choropleth_figure(gdf, col_sum, colorscale, basemap)
    print("figure ended in --- %s seconds ---" % (time.time() - start_time))
    return fig


def _get_regions(regions_fpath, names_col='name:el'):
    if not regions_fpath:
        regions_fpath = 'data/74_regional_units_smooth.geojson' #'/home/blaxeep/Downloads/74_regional_units_kas.geojson'
    gdf = gpd.read_file(regions_fpath)
    gdf[names_col] = gdf[names_col].str.replace('Περιφερειακή Ενότητα ', '')
    return gdf


def _get_necessary_columns_only(dff, x_col, y_col, col_sum):
    # check if regional units is in columns. If it is not, add it manually
    if REGIONAL_UNITS == x_col:
        dff = dff.groupby([x_col])[col_sum].apply(lambda x : x.astype(float).sum())
    else:
        dff = dff.groupby([x_col, y_col, REGIONAL_UNITS])[col_sum].apply(lambda x : x.astype(float).sum())
    dff = dff.reset_index()
    return dff


def _join_data_with_regions(regions_df, dff, col_sum, left_col):
    gdf = pd.merge(regions_df, dff, how='left', left_on=left_col, right_on=REGIONAL_UNITS)
    gdf[col_sum] = gdf[col_sum].fillna(0)
    gdf[col_sum] = pd.to_numeric(gdf[col_sum])
    gdf = gdf[gdf[col_sum] > 0]
    return gdf


def _create_choropleth_figure(gdf, stat_to_show, colorscale, basemap):
    fig = px.choropleth_mapbox(gdf,
                               geojson=gdf['geometry'],
                               locations=gdf.index,
                               color=stat_to_show,
                               color_continuous_scale=colorscale,
                               center={"lat": 38.5517, "lon": 23.7073},
                               mapbox_style=basemap,
                               opacity=0.35,
                               hover_name=REGIONAL_UNITS,
                               height=700,
                               zoom=5)
    return fig


def _create_choropleth_figure_go(gdf, stat_to_show, colorscale, basemap):
    fig = go.Figure(data=go.Choropleth(
        locations = gdf['geometry']
    ))
    pass


def create_prod_cons_file(download_df, download_cons_df):
    """Method to create a productions-consumptions dataframe file
    from the user's given custom parameters.

    Args:
        download_df (Dataframe): Custom productions file
        download_cons_df (Dataframe): Custom consumptions file

    Raises:
        PreventUpdate: [description]

    Returns:
        [Dataframe]: A dataframe with prod-cons data.
    """
    # sum by amounts of products by reguinal units
    prods = download_df.groupby(['Περιφέρειες (NUTS2)', 'Περ. Ενότητες (NUTS3)'])['Ποσότητα (σε τόνους)'].sum().reset_index()
    cons = download_cons_df.groupby(['Περιφέρειες (NUTS2)', 'Περ. Ενότητες (NUTS3)'])['Ποσότητα (σε τόνους)'].sum().reset_index()
    # make an inner join because cons has more regional units
    result = prods.merge(cons, on='Περ. Ενότητες (NUTS3)', how='inner', suffixes=('_prod', '_cons'))
    del result['Περιφέρειες (NUTS2)_cons']
    result.columns = ['ΠΕΡΙΦΕΡΕΙΑ', 'ΠΕΡΙΦΕΡΕΙΑΚΕΣ ΕΝΟΤΗΤΕΣ', 'Παραγωγές (tn)', 'Κατανάλωση']
    return result


def _get_month_range(dff, month_vals):
    """Method to get only selected months from the dataframe.

    Args:
        dff (dataframe): Dataframe that contains data
        month_vals (list): list that contains start and end values

    Raises:
        PreventUpdate: [description]

    Returns:
        [Dataframe]: The dataframe within the range given.
    """
    # if range slider value is the default, just return the dataframe.
    # else, have the range desired as a dataframe and return it.
    if month_vals == [0,0]:
        return dff
    else:
        start_month, end_month = month_vals
        dff = dff[(dff[MONTH] >= int(start_month)) & (dff[MONTH] <= int(end_month))]
        return dff


def _get_filtered_dff(sample_df, x_col, x_col_vals, y_col, y_col_vals, col_sum, selected_matrix, year_val, month_val):
    dff = sample_df[sample_df[x_col].isin(x_col_vals)]
    dff = dff[dff[y_col].isin(y_col_vals)]
    if (year_val):
        dff = dff[dff[REPORT_YEAR] == year_val]
    dff = _get_month_range(dff, month_val)
    dff = _get_necessary_columns_only(dff, x_col, y_col, col_sum)
    return dff



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
                #html.Div(id='year-radio'),
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
                dcc.Dropdown(id='cities-radio',
                             multi=True,
                             options=[]),],
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
                dcc.Dropdown(id='products-radio-val',
                             multi=True,
                             options=[]),],
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
                dcc.Dropdown(id='chart-choice',
                                options=[{'label': k, 'value': k} for k in chart_types],
                                value='Γράφημα Στήλης',
                                ), #labelStyle={'display': 'inline-block', 'text-align': 'justify'}), this is about Radioitems
                html.Button('Καταχώρηση Παραμέτρων', id='submit-val', n_clicks=0, style=white_button_style),
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
    dcc.RangeSlider(
        id='range-slider',
        min=0,
        max=12,
        step=1,
        marks=month_dict,
        value=[0,0]
    ),],  style={'backgroundColor':'#CEFFBD',
               'font-weight': 'bold',
               'fontSize' : '17px',
               'color':'#111111'}),
    
    # graphs here
    html.Hr(),
    dcc.Graph(id='indicator-graphic-multi-sum'),
    html.Hr(),
    # maps here
    html.Div([
            html.Div([
                html.Label("ΔΙΑΘΕΣΙΜΕΣ ΧΡΩΜΑΤΙΚΕΣ ΕΠΙΛΟΓΕΣ",
                    style={'font-weight': 'bold',
                            'fontSize' : '15px',
                            'margin-left':'auto',
                            'margin-right':'auto',
                            'display':'block'}),
                dcc.Dropdown(id='availability-colors',
                            options=[{"value": x, "label": x} 
                                        for x in colorscales],
                            value='speed',
                            style={"display": "block",
                    "margin-left": "auto",
                    "margin-right": "auto",
                    # "width":"60%"
                    }), # style solution here: https://stackoverflow.com/questions/51193845/moving-objects-bar-chart-using-dash-python
            ], className='four columns'),
            html.Div([
                html.Label("ΔΙΑΘΕΣΙΜΑ ΥΠΟΒΑΘΡΑ ΧΑΡΤΩΝ",
                        style={'font-weight': 'bold',
                                'fontSize' : '15px'}),
                dcc.Dropdown(id='availability-maps',
                             options=[{"value":x, "label":x}
                                      for x in basemaps],
                             value='white-bg',),
                html.Button('ΑΠΕΙΚΟΝΙΣΗ ΑΠΟΤΕΛΕΣΜΑΤΩΝ ΣΕ ΧΑΡΤΗ', id='submit-map', n_clicks=0, style=white_button_style),
            ], className='four columns'),
        ], className='row',
                 style= {'padding-left' : '50px'}), # closes the div for first line (matrix and year)
    html.Hr(),
    html.Div(children=[
        dcc.Graph(id='map-fig'),
    ], style = {'display': 'inline-block', 'height': '178%', 'width': '95%'}),
    # end of maps
    html.Button('Δημιουργία Σεναρίου Προς Διερεύνηση', id='csv_to_disk', n_clicks=0),
    html.Div(id='download-link'),
    html.Div(
        [
            html.Button("Αποθήκευση αποτελεσμάτων με βάση τις επιλογές του χρήστη σε αρχείο CSV", id="btn_csv"),
            Download(id="download-dataframe-csv"),
        ],
    ),
    html.Div(
        html.A(html.Button("Μετάβαση στον υπολογισμό μητρώου προέλευσης-προορισμού", className='three columns'),
        href='http://147.102.154.65:8056/'), # https://github.com/plotly/dash-html-components/issues/16
    )
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
    if available_options is None:
        raise PreventUpdate
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
    selectable=True
    sample_df = load_matrix(selected_matrix)
    if not selected_matrix:
        return ""
    else:
        return [{'label': i, 'value': i} for i in sample_df[REPORT_YEAR].unique()]



@app.callback(
    Output('display-selected-table', 'children'),
    [Input('submit-val', 'n_clicks')],
    [State('countries-radio', 'value'),
    State('cities-radio', 'value'),
    State('products-radio', 'value'),
    State('products-radio-val', 'value'),
    State('availability-radio', 'value'),
    State('year-radio', 'value'),
    State('range-slider', 'value')
    ])
def set_display_table(n_clicks, selected_country, selected_city, selected_prod_cat, selected_prod_val, selected_matrix, year_val, month_val):
    dff = get_col_rows_data(selected_country, selected_city, sample_df)
    #if (year_val):
    #    dff = dff[dff[REPORT_YEAR] == year_val]
    dff = _get_month_range(dff, month_val)
    df_temp = get_col_rows_data(selected_prod_cat, selected_prod_val, dff)
    # reduce decimals to two only.
    df_temp = df_temp.round(2)
    global download_df
    download_df = df_temp # remove this if it is not necessary
    # following two lines are for consumptions corresponding file
    global download_cons_df
    download_cons_df = _get_corresponding_cons_df(selected_prod_cat, selected_prod_val)
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
    [Input('submit-val', 'n_clicks')],
    [State('countries-radio', 'value'),
    State('cities-radio', 'value'),
    State('products-radio', 'value'),
    State('products-radio-val', 'value'),
    State('column-sum', 'value'),
    State('chart-choice', 'value'),
    State('availability-radio', 'value'),
    State('year-radio', 'value'),
    State('range-slider', 'value')
    ])
def set_display_figure(n_clicks, x_col, x_col_vals, y_col, y_col_vals, col_sum, chart_type, selected_matrix, year_val, month_val):
    dff = sample_df[sample_df[x_col].isin(x_col_vals)]
    dff = dff[dff[y_col].isin(y_col_vals)]
    if (year_val):
        dff = dff[dff[REPORT_YEAR] == year_val]
    dff = _get_month_range(dff, month_val)
    #dff = _get_necessary_columns_only(dff, x_col, y_col, col_sum)
    
    if chart_type == 'Γράφημα Στήλης':
        fig = get_bar_figure(dff, x_col, col_sum, y_col)
    elif chart_type == 'Γράφημα Πίτας':
        fig = get_pie_figure(dff, x_col, col_sum, y_col)

    return fig


@app.callback(
    Output('map-fig', 'figure'),
    [Input('submit-map', 'n_clicks')],
    [State('countries-radio', 'value'),
    State('cities-radio', 'value'),
    State('products-radio', 'value'),
    State('products-radio-val', 'value'),
    State('column-sum', 'value'),
    State('availability-radio', 'value'),
    State('year-radio', 'value'),
    State('range-slider', 'value'),
    State('availability-colors', 'value'),
    State('availability-maps', 'value'),
    ])
def set_display_map(n_clicks, x_col, x_col_vals, y_col, y_col_vals, col_sum, selected_matrix, year_val, month_val, colorscale, basemap):
    """ Method to print map stats
    """
    dff = _get_filtered_dff(sample_df, x_col, x_col_vals, y_col, y_col_vals, col_sum, selected_matrix, year_val, month_val)
    fig = get_choropleth_figure(dff, x_col, col_sum, colorscale, basemap)
    return fig


@app.callback(
    Output('enhanced-map-fig', 'figure'),
    [Input('submit-map', 'n_clicks')],
    [State('availability-colors', 'value'),
    State('availability-maps', 'value'),
    State('countries-radio', 'value'),
    State('products-radio', 'value'),
    State('column-sum', 'value'),
    ])
def set_enhanced_display_map(n_clicks, colorscale, basemap, x_col, y_col, col_sum):
    """ Method to print map stats
    """
    dff = download_df
    dff = _get_necessary_columns_only(dff, x_col, y_col, col_sum)
    fig = get_choropleth_figure(dff, x_col, col_sum, colorscale, basemap)
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


@app.callback(
    Output('range-output-container-slider', 'children'),
    [Input('range-slider', 'value')]
)
def update_range_slider(value):
    if value == [0, 0]:
        return value
    x = []
    for v in value:
        x.append(int(v))
    return x


@app.callback(Output('download-link', 'children'),
              Input('csv_to_disk', 'n_clicks'),)
def save_df_conf_to_disk(btn_click):
    # compute timestamp and name the filename.
    results_name = _create_results_name()
    fpath = results_path + results_name
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'csv_to_disk' in changed_id:
        custom_prod_cons = create_prod_cons_file(download_df, download_cons_df)
        #download_df.to_csv(fpath, sep='\t')
        custom_prod_cons.to_csv(fpath, sep='\t', index=False)
        msg = 'Δημιουργήθηκε αρχείο παραγωγών-καταναλώσεων με όνομα ' + results_name
    else:
        msg = 'Δεν αποθηκεύθηκαν οι αλλαγές σε αρχείο.'
    return html.Div(msg)


@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return send_data_frame(download_df.to_csv, "mydf.csv") # dash_extensions.snippets: send_data_frame


if __name__ == "__main__":
    app.run_server(debug=False,port=8054) #  host='147.102.154.65', 