""" module to highlight certain cells to dash table.

source: https://dash.plotly.com/datatable/conditional-formatting
"""


import dash
import dash_table
import pandas as pd
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

app = dash.Dash(__name__)

df['id'] = df.index

app.layout = dash_table.DataTable(
    data=df.to_dict('records'),
    sort_action='native',
    columns=[{'name': i, 'id': i} for i in df.columns if i != 'id'],
    style_table={'height':'800px', 'overflowY':'auto'},
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold'
    },
    style_data_conditional=highlight_max_row(df)
)


if __name__ == '__main__':
    app.run_server(debug=True)