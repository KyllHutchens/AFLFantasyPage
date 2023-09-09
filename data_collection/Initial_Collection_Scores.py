from bs4 import BeautifulSoup
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
import csv
import requests
from lxml import html


load_dotenv()

connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
def get_footywire_ids():
    try:
        cur = connection.cursor()
        cur.execute("SELECT footywire_id FROM fixture;")
        results = cur.fetchall()
        cur.close()
        return [result[0] for result in results]

    except Exception as e:
        print(f"Error occurred: {e}")
        return []

footywire_ids = get_footywire_ids()


def fetch_content(footywire_id):
    # Construct the URL (Modify this if the structure of your URL is different)
    url = f"https://www.footywire.com/afl/footy/ft_match_statistics?mid={footywire_id}"

    # Request the webpage
    response = requests.get(url)
    response.raise_for_status()

    # Parse the webpage with lxml
    tree = html.fromstring(response.content)

    # Try to get the text content using the specified XPath
    content = tree.xpath('//*[@id="matchscoretable"]/tbody/tr[2]/td[1]/a/text()')

    if not content:
        print(f"No content found for footywire_id: {footywire_id}")
    else:
        # Print the retrieved text
        print(content[0])

# Test the function with your first footywire_id
fetch_content(footywire_ids[0])