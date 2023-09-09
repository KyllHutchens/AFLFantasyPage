import requests
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
import csv
from dotenv import load_dotenv

load_dotenv()

#Live games are avaliable at https://www.footywire.com/afl/footy/live_stats?mid={match_id}
connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

team_change_dict = {
    "GWS Giants": "GWS",
    "North Melbourne": "Kangaroos"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
matchid_df = ["10965"]
for row in matchid_df:
    url = f"https://www.footywire.com/afl/footy/live_stats?mid={row}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.select_one("#liveScoreboard table")

if table:
    rows = table.find_all('tr')
    data_list = []
    for row in rows:
        columns = row.find_all('td')
        data_row = [col.text.strip() for col in columns]
        data_list.append(data_row)
    
    # Converting the data list into a pandas DataFrame
    df = pd.DataFrame(data_list)
    df = df.drop([0, 1]).reset_index(drop=True)
    
    # Set the third row (now the first row) as headers
    df.columns = df.iloc[0]
    df = df.drop(0).reset_index(drop=True)
    team1 = df.iloc[0, 0]
    team2 = df.iloc[1, 0]
    team1 = team_change_dict.get(team1, team1)
    team2 = team_change_dict.get(team2, team2)

    print(team1)
    print(team2)

else:
    print("Table not found using the given selector.")

all_rows = []

for row in matchid_df:
    url = f"https://www.footywire.com/afl/footy/live_stats?mid={row}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    # Mapping selectors to their respective team names for easier iteration
    selectors_teams = {
        "#team1Stats table": team1,
        "#team2Stats table": team2
    }

    for table_selector, team in selectors_teams.items():
        tables = soup.select(table_selector)
        if tables and len(tables) > 1:
            target_table = tables[1]
            for row_idx, table_row in enumerate(target_table.find_all('tr')):
                if row_idx == 0:
                    continue
                values = [td.get_text(strip=True) for td in table_row.find_all('td')]
                all_rows.append([row, team] + values)  # Add the 'team' variable here
        else:
            print(f"Target table not found for match_id: {row} using selector {table_selector}.")
col_names = ['footywire_id', 'team', 'player_number', 'name', 'k', 'hb', 'd', 'm', 'g', 'b', 't', 'ho', 'ga', 'i50', 'cl', 'cg', 'r50', 'ff', 'fa', 'af', 'sc']

final_df = pd.DataFrame(all_rows, columns=col_names)
query = 'SELECT id, team, player_number FROM players'
players_df = pd.read_sql(query, connection)
final_df['player_number'] = final_df['player_number'].astype(int)
players_df['player_number'] = players_df['player_number'].astype(int)

# Now, you can merge them
final_df = pd.merge(final_df, players_df, on=['team', 'player_number'], how='left')

cur = connection.cursor()
# Iterate over DataFrame rows and insert/update data
for _, row in final_df.iterrows():
    insert_update_query = """
    INSERT INTO transaction_temp_data (footywire_id, team, player_number, name, k, hb, d, m, g, b, t, ho, ga, i50, cl, cg, r50, ff, fa, af, sc, player_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (footywire_id, player_id)
    DO UPDATE SET
        team = EXCLUDED.team,
        player_number = EXCLUDED.player_number,
        name = EXCLUDED.name,
        k = EXCLUDED.k,
        hb = EXCLUDED.hb,
        d = EXCLUDED.d,
        m = EXCLUDED.m,
        g = EXCLUDED.g,
        b = EXCLUDED.b,
        t = EXCLUDED.t,
        ho = EXCLUDED.ho,
        ga = EXCLUDED.ga,
        i50 = EXCLUDED.i50,
        cl = EXCLUDED.cl,
        cg = EXCLUDED.cg,
        r50 = EXCLUDED.r50,
        ff = EXCLUDED.ff,
        fa = EXCLUDED.fa,
        af = EXCLUDED.af,
        sc = EXCLUDED.sc;
    """
    
    cur.execute(insert_update_query, tuple(row))
connection.commit()



