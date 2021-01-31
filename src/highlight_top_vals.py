import dash
import dash_table
import pandas as pd
import pdb

#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
df = pd.read_csv('data/OD2019.csv')

app = dash.Dash(__name__)

app.layout = dash_table.DataTable(
    data=df.to_dict('records'),
    columns=[
        {"name": i, "id": i} for i in df.columns
    ],

    style_data_conditional=(
        [
            {
                'if': {
                    'filter_query': '{{EL301}} = {}'.format(i),
                    'column_id': 'EL301',
                },
                'backgroundColor': '#0074D9',
                'color': 'white'
            }
            for i in df['EL301'].nlargest(3)
        ] +
        [
            {
                'if': {
                    'filter_query': '{{EL302}} = {}'.format(i),
                    'column_id': 'EL302',
                },
                'backgroundColor': '#7FDBFF',
                'color': 'white'
            }
            for i in df['EL302'].nsmallest(3)
        ]
    )
)

if __name__ == '__main__':
    app.run_server(debug=True)
