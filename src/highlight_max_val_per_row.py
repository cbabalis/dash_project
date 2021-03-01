""" module to highlight certain cells to dash table.

source: https://dash.plotly.com/datatable/conditional-formatting
"""


import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go

import pdb


def highlight_max_row(df):
    df_numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
    return [
        {
            'if': {
                'filter_query': '{{id}} = {}'.format(i),
                'column_id': col
            },
            'backgroundColor': '#3D9970',
            'color': 'white'
        }
        # idxmax(axis=1) finds the max indices of each row
        for (i, col) in enumerate(
            df_numeric_columns.idxmax(axis=1)
        )
    ]

def highlight_above_and_below_max(df):
    df_numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
    mean = df_numeric_columns.mean().mean()
    return (
        [
            {
                'if': {
                    'filter_query': '{{{}}} > {}'.format(col, mean),
                    'column_id': col
                },
                'backgroundColor': '#3D9970',
                'color': 'white'
            } for col in df_numeric_columns.columns
        ] +
        [
            {
                'if': {
                    'filter_query': '{{{}}} <= {}'.format(col, mean),
                    'column_id': col
                },
                'backgroundColor': '#FF4136',
                'color': 'white'
            } for col in df_numeric_columns.columns
        ]
    )


df = pd.read_csv('data/OD2019.csv')


def get_top_production_by_region(df, how_many_vals=15):
    if 'Unnamed: 0' in df.columns:
        df = df.drop(columns=['Unnamed: 0'])
    df['sum'] = df.drop('Unnamed: 1', axis=1).sum(axis=1)
    top_prods = df[['Unnamed: 1', 'sum']]
    top_prods = top_prods.nlargest(how_many_vals, 'sum')
    return top_prods


def create_top_sums_by_region(df, how_many_sums=15):
    rows_sum = df.sum(numeric_only=True, axis=1).tolist()
    cols_sum = df.sum(numeric_only=True, axis=0).tolist()
    nuts = df.columns.tolist()
    nuts = [x for x in nuts if not x.startswith('Unnamed')]
    stats_df = pd.DataFrame({
        'nuts':nuts,
        'cols_sum': cols_sum,
        'rows_sum': rows_sum})
    return stats_df


def create_unique_prefix_list(a_df, pref='EL'):
    nuts = a_df.columns.tolist()
    prefixes = []
    for word in nuts:
        if word.startswith(pref):
            prefixes.append(word[0:4])
    prefixes = set(prefixes)
    return list(prefixes)


def get_region_stats(a_df, prefixes, name='nuts'):
    cols_list = []
    rows_list = []
    for prefix in prefixes:
        prefix_df = a_df[a_df[name].str.contains(prefix)]
        cols, rows = prefix_df.sum(numeric_only=True, axis=0).tolist()
        cols_list.append(cols)
        rows_list.append(rows)
    regions_df = pd.DataFrame({
        'nuts':prefixes,
        'cols_sum': cols_list,
        'rows_sum': rows_list})
    return regions_df

#top_prods = get_top_production_by_region(df)
stats_df = create_top_sums_by_region(df)
prods_df = stats_df.nlargest(15, 'rows_sum')
cons_df = stats_df.nlargest(15, 'cols_sum')
filter_row = create_unique_prefix_list(df)
reg_df = get_region_stats(stats_df, filter_row)


def get_pie(a_df, val, my_title=''):
    trace = go.Pie(labels=a_df['nuts'].tolist(),
                    values=a_df[val].tolist(),
                    title=my_title)
    data = [trace]
    fig = go.Figure(data = data)
    return fig


app = dash.Dash(__name__)

df['id'] = df.index

features = df.columns

app.layout = html.Div([
    html.H1('Εφαρμογή Δεδομένων και Διαγραμμάτων', style={'textAlign':'center',
                                'color':'#7FDBFF'}),
    html.H3('Επιλέξτε στήλες προς προβολή'),
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
    html.Br(),
    html.H2('Πίνακας Δεδομένων', style={'textAlign':'center'}),
    dash_table.DataTable(
        data=df.to_dict('records'),
        sort_action='native',
        columns=[{'name': i, 'id': i} for i in df.columns if i != 'id'],
        style_table={'height':'800px', 'overflowY':'auto'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_data_conditional=highlight_max_row(df)
    ),
    html.Hr(),
    html.H2('Διαγράμματα και Στατιστικά'),
    html.Div([
        dcc.Graph(id='bar-graph-prod',
            figure={
                'data':[
                    {'x':prods_df['nuts'], 'y':prods_df['rows_sum'],
                    'type':'bar'},
                ],
                'layout':{'title': 'Μεγαλύτερες Παραγωγές ανά περιοχή'}
            })
        ], style={'padding':10, 'width':'45%', 'display':'inline-block'},),
    html.Div([
        dcc.Graph(id='bar-graph-cons',
            figure={
                'data':[
                    {'x':cons_df['nuts'], 'y':cons_df['rows_sum'],
                    'type':'bar'},
                ],
                'layout':{'title': 'Μεγαλύτερες Καταναλώσεις ανά περιοχή'}
            })
        ], style={'padding':10, 'width':'45%', 'display':'inline-block'},),
    html.Br(),
    html.Div([
        dcc.Graph(id='bar-pie-prod',
        figure= get_pie(reg_df, 'rows_sum', my_title='Παραγωγή ανά περιφέρεια')),
        ], style={'padding':10, 'width':'45%', 'display':'inline-block'},),
     html.Div([
        dcc.Graph(id='bar-pie-con',
        figure= get_pie(reg_df, 'cols_sum', my_title='Κατανάλωση ανά περιφέρεια')),
        ], style={'padding':10, 'width':'45%', 'display':'inline-block'},),
    ])


if __name__ == '__main__':
    #app.run_server(debug=True, host='147.102.154.65', port=8053)
    app.run_server(debug=True)
