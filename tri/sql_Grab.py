## From SQL to DataFrame Pandas
import pandas as pd
import pyodbc
import sqlite3 as db 
from pandas.io import sql
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from pandas_datareader.data import DataReader
import plotly.graph_objs as go
from dash.dependencies import Input,Output, Event


first_load = 0

# cnx = db.connect('./tri/test.sqlite')
# df = [] 

# if first_load == 1: 

#     sql_conn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
#                         "Server=TARTRRG06SQLLRT;"
#                         "Database=tridev;"
#                         "UID=tritest;"
#                         "PWD=tritest;")

#     query = "SELECT top 100 * from T_TRIPEOPLE"
#     df = pd.read_sql(query, sql_conn)
#     df.to_sql('T_TRIPEOPLE',cnx,if_exists='replace',index=True)


app = dash.Dash('ehs_inspectors')
app.layout = html.Div(children=[
    html.H1('''
    ehs_inspectors
    '''),
    dcc.Input(id='input', value='', type='text'),
    html.Div(id='output-graph')
])


@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='input', component_property='value')]
)

def update_graph():
    query = "SELECT * FROM tab;"
    cnx = db.connect('./tri/test.sqlite')
    df2 = pd.read_sql_query(query, cnx)
    print(df2.head(10))
    '''usually SQL query here'''
    dcc.Graph(id='example-graph',
            figure={
                'data': [
                    {'x': df2.TRINAMETX, 'y': df2.SPEC_ID, 'type': 'line', 'name': 'test1'}
                ],
                'layout': {
                    'title': 'test1'
                }
            })



if __name__ == "__main__":
    app.run_server(debug=True)
