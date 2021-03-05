import random
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash_table import DataTable
from dash.exceptions import PreventUpdate
import pandas as pd

sample_df = pd.DataFrame({
    'int': [random.randint(1, 100) for i in range(20)],
    'float': [random.random() * x for x in random.choices(range(100), k=20)],
    'str(object)': ['one', 'one two', 'one two three', 'four'] * 5,
    'category': random.choices(['Sat', 'Sun', 'Mon', 'Tue', 'Wed','Thu', 'Fri'], k=20),
    'datetime': pd.date_range('2019-05-01', periods=20),
    'bool': random.choices([True, False], k=20),
})
sample_df['category'] = sample_df['category'].astype('category')


def get_str_dtype(df, col):
    """Return dtype of col in df"""
    dtypes = ['datetime', 'bool', 'int', 'float',
              'object', 'category']
    for d in dtypes:
        if d in str(df.dtypes.loc[col]).lower():
            return d


app = dash.Dash(__name__)


app.layout = html.Div([
    html.Div([
        html.Div(id='container_col_select',
                 children=dcc.Dropdown(id='col_select',
                                       options=[{
                                           'label': c.replace('_', ' ').title(),
                                           'value': c}
                                           for c in sample_df.columns]),
                 style={'display': 'inline-block', 'width': '30%', 'margin-left': '7%'}),
        # DataFrame filter containers
        html.Div([
            html.Div(children=dcc.RangeSlider(id='num_filter',
                                              updatemode='drag')),
            html.Div(children=html.Div(id='rng_slider_vals'), ),
        ], id='container_num_filter', ),
        html.Div(id='container_str_filter',
                 children=dcc.Input(id='str_filter')),
        html.Div(id='container_bool_filter',
                 children=dcc.Dropdown(id='bool_filter',
                                       options=[{'label': str(tf), 'value': tf}
                                                for tf in [True, False]])),
        html.Div(id='container_cat_filter',
                 children=dcc.Dropdown(id='cat_filter', multi=True,
                                       options=[{'label': day, 'value': day}
                                                for day in sample_df['category'].unique()])),
        html.Div([
            dcc.DatePickerRange(id='date_filter',
                                initial_visible_month= pd.datetime(2019, 5, 10)),
        ], id='container_date_filter'),
    ]),

    DataTable(id='table',
              columns=[{"name": i, "id": i} for i in sample_df.columns],
              style_cell={'maxWidth': '400px', 'whiteSpace': 'normal'},
              data=sample_df.to_dict("rows"))
])


@app.callback([Output(x, 'style')
               for x in ['container_num_filter', 'container_str_filter',
                         'container_bool_filter', 'container_cat_filter',
                         'container_date_filter']],
              [Input('col_select', 'value')])
def dispaly_relevant_filter_container(col):
    if col is None:
        return [{'display': 'none'} for i in range(5)]
    dtypes = [['int', 'float'], ['object'], ['bool'],
              ['category'], ['datetime']]
    result = [{'display': 'none'} if get_str_dtype(sample_df, col) not in d
              else {'display': 'inline-block',
                    'margin-left': '7%',
                    'width': '400px'} for d in dtypes]
    return result


@app.callback([Output('date_filter', 'start_date'),
               Output('date_filter', 'end_date'),
               Output('date_filter', 'min_date_allowed'),
               Output('date_filter', 'max_date_allowed'),],
              [Input('col_select', 'value')])
def set_date_filter_params(col):
    if col is None:
        raise PreventUpdate
    start = sample_df[col].min()
    end = sample_df[col].max()
    return start, end, start, end

@app.callback(Output('rng_slider_vals', 'children'),
              [Input('num_filter', 'value')])
def show_rng_slider_max_min(numbers):
    if numbers is None:
        raise PreventUpdate
    return 'from:' + ' to: '.join([str(numbers[0]), str(numbers[-1])])


@app.callback([Output('num_filter', 'min'),
               Output('num_filter', 'max'),
               Output('num_filter', 'value')],
              [Input('col_select', 'value')])
def set_rng_slider_max_min_val(column):
    if column is None:
        raise PreventUpdate
    if column and (get_str_dtype(sample_df, column) in ['int', 'float']):
        minimum = sample_df[column].min()
        maximum = sample_df[column].max()
        return minimum, maximum, [minimum, maximum]
    else:
        return None, None, None


@app.callback(Output('table', 'data'),
              [Input('col_select', 'value'),
               Input('num_filter', 'value'),
               Input('cat_filter', 'value'),
               Input('str_filter', 'value'),
               Input('bool_filter', 'value'),
               Input('date_filter', 'start_date'),
               Input('date_filter', 'end_date')])
def filter_table(col, numbers, categories, string,
                 bool_filter, start_date, end_date):
    if all([param is None for param in [col, numbers, categories,
                                        string, bool_filter, start_date,
                                        end_date]]):
        raise PreventUpdate
    if numbers and (get_str_dtype(sample_df, col) in ['int', 'float']):
        df = sample_df[sample_df[col].between(numbers[0], numbers[-1])]
        return df.to_dict('rows')
    elif categories and (get_str_dtype(sample_df, col) == 'category'):
        df = sample_df[sample_df[col].isin(categories)]
        return df.to_dict('rows')
    elif string and get_str_dtype(sample_df, col) == 'object':
        df = sample_df[sample_df[col].str.contains(string, case=False)]
        return df.to_dict('rows')
    elif (bool_filter is not None) and (get_str_dtype(sample_df, col) == 'bool'):
        df = sample_df[sample_df[col] == bool_filter]
        return df.to_dict('rows')
    elif start_date and end_date and (get_str_dtype(sample_df, col) == 'datetime'):
        df = sample_df[sample_df[col].between(start_date, end_date)]
        return df.to_dict('rows')
    else:
        return sample_df.to_dict('rows')

if __name__ == '__main__':
    app.run_server(debug=True)