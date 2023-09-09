
import psycopg2
import os
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
cursor = connection.cursor()

game_ids = ['10951','10953','10954','10949', '10952', '10957', '10956', '10955', '10950']
for id_value in game_ids:
    update_query = """
    WITH updated_rows AS (
        SELECT fixture_id
        FROM fixture
        WHERE footywire_id IS NULL
        LIMIT 1
        FOR UPDATE
    )
    UPDATE fixture
    SET footywire_id = %s
    FROM updated_rows
    WHERE fixture.fixture_id = updated_rows.fixture_id;
    """
    cursor.execute(update_query, (id_value,))
    connection.commit()

cursor.close()
connection.close()