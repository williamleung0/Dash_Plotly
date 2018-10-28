import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
import pandas_datareader.data as web
import datetime
import fix_yahoo_finance as yf
yf.pdr_override()

start = datetime.datetime(2015, 1, 1)
end = datetime.datetime.now()
stock = 'AMZN'
data_source = 'yahoo'

df = web.get_data_yahoo(stock, start, end)
app = dash.Dash()

app.layout = html.Div(children=[
    html.H1('''
        symbol to graph
    '''),
    dcc.Input(id='input', value='', type='text'),
    html.Div(id='output-graph')
])


@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='input', component_property='value')]
)
def update_graph(input_data):
    start = datetime.datetime(2015, 1, 1)
    end = datetime.datetime.now()
    df = web.get_data_yahoo(input_data, start, end)
    return dcc.Graph(id='example-graph',
              figure={
                  'data': [
                      {'x': df.index, 'y': df.Close, 'type': 'line', 'name': input_data}
                  ],
                  'layout': {
                      'title': input_data
                  }
              })


def update_value(input_data):
    try:
        return str(float(input_data)**2)
    except:
        return 'some error'


if __name__ == '__main__':
    app.run_server(debug=True)
