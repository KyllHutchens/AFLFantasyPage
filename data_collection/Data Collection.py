import requests
from bs4 import BeautifulSoup
import pandas as pd

# Read the CSV containing match IDs into a dataframe
match_ids_df = pd.read_csv('R23Fixture.csv')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

all_rows = []
columns = None

for _, row in match_ids_df.iterrows():
    match_id = row['GameID']
    round_number = row['round.roundNumber']
    season_year = row['compSeason.year']
    home_team = row['home.team.name']
    away_team = row['away.team.name']
    start_time = row['utcStartTime']

    url = f"https://www.footywire.com/afl/footy/ft_match_statistics?mid={match_id}"
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    for idx, table_selector in enumerate(["#match-statistics-team1-row table", "#match-statistics-team2-row table"]):
        team_name = home_team if idx == 0 else away_team
        opposing_team = away_team if idx == 0 else home_team
        team_role = "Home" if idx == 0 else "Away"
        
        tables = soup.select(table_selector)
        if tables and len(tables) > 1:
            target_table = tables[2]
            for table_row in target_table.find_all('tr'):
                values = [td.get_text(strip=True) for td in table_row.find_all('td')]
                
                # If it's the header row, update the columns list
                if not columns:
                    columns = ["Team", "Role", "Opposing Team", "Round Number", "Season Year", "Start Time"] + values
                else:
                    # Add team details before the actual data
                    all_rows.append([team_name, team_role, opposing_team, round_number, season_year, start_time] + values)
        else:
            print(f"Target table not found for match_id: {match_id} using selector {table_selector}.")

# Convert all rows to a DataFrame at the end
final_df = pd.DataFrame(all_rows, columns=columns)
print(final_df)
