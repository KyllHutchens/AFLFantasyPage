from dash import dcc
from dash import html
import dash.dependencies as dd
import requests

# Define the layout for your dashboard
layout = html.Div(children=[
    dcc.Dropdown(
        id='player-dropdown',
        options=[],  # Initially empty
        value=None,
        multi=False,
        placeholder="Select a Player"
    ),
    dcc.Graph(id='player-stats-graph'),
])

def register_callbacks(app):
    """Register Dash callbacks for interactive components."""
    
    @app.callback(
        dd.Output('player-dropdown', 'options'),
        dd.Input('player-dropdown', 'value')
    )
    def update_dropdown_options(_):
        """Fetch all players from the backend to populate the dropdown."""
        response = requests.get('http://127.0.0.1:5000/getPlayers')
        players = response.json()
        
        # Sort players by team first and then by player name
        sorted_players = sorted(players, key=lambda x: (x[1], x[0]))

        # Create dropdown options using sorted players
        return [{'label': f"{player[0]} - {player[1]}", 'value': player[0]} for player in sorted_players]

    @app.callback(
        dd.Output('player-stats-graph', 'figure'),
        [dd.Input('player-dropdown', 'value')]
    )
    def update_graph(player_name):
        """Fetch player data and update the graph based on dropdown selection."""
        if not player_name:
            return {}

        # Fetch player data from the backend based on dropdown selection
        response = requests.get(f'http://127.0.0.1:5000/getPlayerData/{player_name}')
        if response.status_code != 200:
            print(f"Unexpected status code {response.status_code}: {response.text}")
            data = []  # or some other default value
        else:
            data = response.json()
        # Ensure the data is in the right format
        if not all(isinstance(item, (list, tuple)) and len(item) == 2 for item in data):
            # Return an empty figure if the data format is unexpected
            return {}

        rounds = [item[0] for item in data]
        points = [item[1] for item in data]

        return {
            'data': [{'x': rounds, 'y': points, 'type': 'line', 'name': player_name}],
            'layout': {
                'title': f'Fantasy Points for {player_name}',
                'xaxis': {
                    'title': 'Rounds',
                    'range': [1, 23],  # Restricting x axis from 1 to 23
                    'tickvals': list(range(1, 24))  # Setting tick values for clarity
                },
                'yaxis': {
                    'title': 'Points',
                    'range': [0, 200],  # Restricting y axis from 0 to 200
                },
                'showlegend': True
            }
        }
