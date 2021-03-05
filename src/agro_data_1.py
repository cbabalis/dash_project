import base64
import os
from urllib.parse import quote as urlquote

from flask import Flask, send_from_directory
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px


df = pd.read_csv('data/agro2018/Agro2018_no_nanBABIS.csv', delimiter='\t')


UPLOAD_DIRECTORY = "data/"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
server = Flask(__name__)
app = dash.Dash(server=server)

product_dpdown = []
for i in df['Αγροτικά Προϊόντα'].unique() :
   str(product_dpdown.append({'label':i,'value':(i)}))


region_dpdown = []
for i in df['Περιφέρεια (NUTS 2)'].unique() :
   str(region_dpdown.append({'label':i,'value':(i)}))



@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


app.layout = html.Div(
    [
        html.H1("Εφαρμογή Δεδομένων και Διαγραμμάτων",  style={'textAlign':'center'}),
        html.Hr(),
        html.P([
             html.Label("Επιλέξτε προϊόν:"),
             html.Div(dcc.Dropdown(id='product_dp', options=product_dpdown),
                                style = {'width': '250px',
                                    'fontSize' : '15px',
                                    'padding-left' : '10px',
                                    'padding-right' : '100px',
                                    'display': 'inline-block'}),
             html.Label("Επιλέξτε Περιφερειακή Ενότητα:"),
             html.Div(dcc.Dropdown(id='region_dp', options=region_dpdown),
                                style = {'width': '250px',
                                    'fontSize' : '15px',
                                    'padding-left' : '10px',
                                    'display': 'inline-block'})]),
        html.Hr(),
        html.H2("Πίνακας Δεδομένων"),
    #     dash_table.DataTable(
    #     id='datatable-interactivity',
    #     columns=[
    #         {"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
    #     ],
    #     data=df.to_dict('records'),
    #     editable=True,
    #     filter_action="native",
    #     sort_action="native",
    #     sort_mode="multi",
    #     column_selectable="single",
    #     row_selectable="multi",
    #     row_deletable=True,
    #     selected_columns=[],
    #     selected_rows=[],
    #     page_action="native",
    #     page_current= 0,
    #     page_size= 10,
    # ),
    html.Div(id='datatable-interactivity',  className='tableDiv'),

    html.H2("Διαγράμματα"),
    html.Div(id='datatable-interactivity-container'),
    html.Hr(),
        html.H3('Διαδραστικά Διαγράμματα'),
        html.Div([
            dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in df.columns],
                value='Περιφέρεια (NUTS 2)'
            ),
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in df.columns],
                value='Κατηγορία Αγροτικών Προϊόντων',
            )
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'}),
    html.Br(),
    html.Hr(),
    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
        )
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Hr(),
    html.H2("Περιοχή ανεβάσματος αρχείου από τον δίσκο"),
        dcc.Upload(
            id="upload-data",
            children=html.Div(
                ["Σύρετε αρχείο ή κάντε κλικ για να ανεβάσετε αρχείο από τον δίσκο."]
            ),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=True,
        ),
        html.H2("Αρχεία στη Βάση"),
        html.Ul(id="file-list"),
        # table here
    ],
    style={"max-width": "1000px"},
)


def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


@app.callback(
    Output("file-list", "children"),
    [Input("upload-data", "filename"), Input("upload-data", "contents")],
)
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)

    files = uploaded_files()
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        return [html.Li(file_download_link(filename)) for filename in files]



@app.callback(
    Output('datatable-interactivity', 'style_data_conditional'),
    Input('datatable-interactivity', 'selected_columns')
)
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

@app.callback(
    Output('datatable-interactivity-container', "children"),
    Input('datatable-interactivity', "derived_virtual_data"),
    Input('datatable-interactivity', "derived_virtual_selected_rows"))
def update_graphs(rows, derived_virtual_selected_rows):
    # When the table is first rendered, `derived_virtual_data` and
    # `derived_virtual_selected_rows` will be `None`. This is due to an
    # idiosyncrasy in Dash (unsupplied properties are always None and Dash
    # calls the dependent callbacks when the component is first rendered).
    # So, if `rows` is `None`, then the component was just rendered
    # and its value will be the same as the component's dataframe.
    # Instead of setting `None` in here, you could also set
    # `derived_virtual_data=df.to_rows('dict')` when you initialize
    # the component.
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []

    dff = df if rows is None else pd.DataFrame(rows)

    colors = ['#7FDBFF' if i in derived_virtual_selected_rows else '#0074D9'
              for i in range(len(dff))]

    return [
        dcc.Graph(
            id=column,
            figure={
                "data": [
                    {
                        "x": dff["Περιφέρεια (NUTS 2)"],
                        "y": dff[column],
                        "type": "bar",
                        "marker": {"color": colors},
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
        for column in ["Ποσότητα Παραγωγής (σε τόνους)", "Κατηγορία Αγροτικών Προϊόντων", "Αγροτικά Προϊόντα"] if column in dff
    ]


@app.callback(
    dash.dependencies.Output('datatable-interactivity','children'),
    [dash.dependencies.Input('product_dp', 'value'),
    dash.dependencies.Input('region_dp', 'value')])

def display_table(product_dpdown, region_dpdown):
    df_protemp = df[df['Αγροτικά Προϊόντα']==product_dpdown]
    df_temp = df_protemp[df_protemp['Περιφέρεια (NUTS 2)']==region_dpdown]
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
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name):
    dff = df#[df['Year'] == year_value]

    fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
            y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
            hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name']
            )
    fig.update_traces(customdata=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    return fig


if __name__ == "__main__":
    app.run_server(debug=True, host='147.102.154.65', port=8054)