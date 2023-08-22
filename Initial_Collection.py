import requests
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

query = "SELECT * FROM fixture WHERE fixture_id BETWEEN 2 AND 23;"
match_ids_df = pd.read_sql(query, connection)
connection.close()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

all_rows = []

for _, row in match_ids_df.iterrows():
    match_id = row['footywire_id']
    url = f"https://www.footywire.com/afl/footy/ft_match_statistics?mid={match_id}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    for table_selector in ["#match-statistics-team1-row table", "#match-statistics-team2-row table"]:
        tables = soup.select(table_selector)
        if tables and len(tables) > 1:
            target_table = tables[2]
            for row_idx, table_row in enumerate(target_table.find_all('tr')):
                if row_idx == 0:
                    continue

                values = [td.get_text(strip=True) for td in table_row.find_all('td')]
                all_rows.append([match_id] + values)
        else:
            print(f"Target table not found for match_id: {match_id} using selector {table_selector}.")

final_df = pd.DataFrame(all_rows)

# Create a dictionary to map footywire_id to fixture_id
footywire_to_fixture_id = match_ids_df.set_index('footywire_id')['fixture_id'].to_dict()
final_df['fixture_id'] = final_df[0].map(footywire_to_fixture_id)  # The first column temporarily holds the match_id
final_df.drop(columns=[0], inplace=True)  # Remove the temporary match_id column

player_ids = range(1, len(final_df) + 1)
final_df.insert(0, 'playerid', player_ids)  # Add player ids

# Manually set the columns
final_df.columns = ['playerid', 'Player', 'K', 'HB', 'D', 'M', 'G', 'B', 'T', 'HO', 'GA', 'I50', 'CL', 'CG', 'R50', 'FF', 'FA', 'AF', 'SC', 'fixture_id']

final_df.to_csv('temp.csv', index=False)

# Connect to the database again
connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = connection.cursor()
with open('temp.csv', 'r') as f:
    f.readline()  # skip the header
    cursor.copy_from(f, 'playerstats', sep=',', null="")

connection.commit()
cursor.close()
connection.close()

print("Data inserted successfully!")
