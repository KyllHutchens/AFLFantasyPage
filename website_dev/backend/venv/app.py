from flask import Flask
import dash
import dash_core_components as dcc
from dash import html
from flask_cors import CORS

server = Flask(__name__)
CORS(server, resources={r"/*": {"origins": "http://localhost:3000"}})

@server.route('/')
def hello():
    response = Flask.make_response('Hello from Flask!')
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    return response

app = dash.Dash(__name__, server=server, routes_pathname_prefix='/dash/')
@app.server.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    return response


app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])

if __name__ == '__main__':
    server.run(debug=True)
