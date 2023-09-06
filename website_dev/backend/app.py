from flask import Flask, jsonify, Response
import dash
import psycopg2 
import os
import json
from dashboard_layout import layout, register_callbacks
from dotenv import load_dotenv
from flask_cors import CORS


load_dotenv()

connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

server = Flask(__name__)
CORS(server, resources={r"*": {"origins": "http://localhost:3000"}})

app = dash.Dash(__name__, server=server, routes_pathname_prefix='/dash/')
app.layout = layout

register_callbacks(app)

@server.route('/')
def hello():
    return 'Hello from Flask!'
@server.route('/getPlayers')
def get_players():
    try:
        cur = connection.cursor()

        # Joining the playerstats and players tables to get both player name and team
        query = """
            SELECT ps.player, p.team
            FROM playerstats ps
            JOIN players p ON ps.player = p.full_name
            GROUP BY ps.player, p.team
            ORDER BY p.team, ps.player;
        """
        cur.execute(query)
        
        players = cur.fetchall()
        cur.close()
        return jsonify(players)
    except Exception as e:
        server.logger.error(f"Error while fetching players: {e}")
        return Response("Failed to fetch players.", status=500)

@server.route('/getPlayerData/<player_name>')
def get_player_data(player_name):
    try:
        cur = connection.cursor()
        query = """
    SELECT f.round_number, ps.af 
    FROM playerstats ps 
    JOIN fixture f ON ps.fixture_id = f.fixture_id 
    WHERE ps.player = %s 
    ORDER BY f.round_number
    """
        cur.execute(query, (player_name,))
        data = cur.fetchall()
        cur.close()
        return jsonify(data)
    except Exception as e:
        server.logger.error(f"Error while fetching data for {player_name}: {e}")
        return Response(f"Failed to fetch data for {player_name}.", status=500)

if __name__ == '__main__':
    server.run(debug=True)
