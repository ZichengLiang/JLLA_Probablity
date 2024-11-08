import os
import requests
from bs4 import BeautifulSoup
import time

mainPageURL = "https://fbref.com/en/comps/9/Premier-League-Stats"
numberTeams = 20
teams = []
players = []

def save_html(url, fileName, directory='./data'):
    os.makedirs(directory, exist_ok=True)
    try:
        pageData = requests.get(url)
        pageData.raise_for_status()
        with open(f"{directory}/{fileName}", 'wb') as f:
            f.write(pageData.content)
    except requests.RequestException as e:
        print(f"Error saving HTML from {url}: {e}")

def read_html(pathToFile):
    try:
        with open(pathToFile, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        print(f"File {pathToFile} not found.")
        return None

def extractURLandNames():
    homepage_content = read_html("data/homepage.html")
    if not homepage_content:
        print("Failed to read homepage HTML.")
        return
    
    soup = BeautifulSoup(homepage_content, 'html.parser')
    rows = soup.select('#results2024-202591_overall > tbody > tr')
    
    for row in rows:
        team_link = row.select_one("td[data-stat='team'] a")
        if team_link:
            team_name = team_link.text.strip()
            team_url = "https://fbref.com" + team_link['href']
            
            if team_name == "Nott'ham Forest":
                team_name = "Nottingham Forest"
            
            teams.append(Team(team_name, team_url))

class Team:
    def __init__(self, name, url):
        self.name = name
        self.url = url
    
    def __str__(self):
        return f"{self.name} : {self.url}"

class Player:
    def __init__(self, name, url, position, team):
        self.name = name
        self.url = url
        self.position = position
        self.team = team
        self.Goalkeeper = (position == "GK")
    
    def __str__(self):
        return f"{self.name} : {self.url} : {self.position} : {self.team}"

def saveTeamHTML():
    for team in teams:
        print(f"Saving data for {team.name}")
        save_html(team.url, f"{team.name}.html", "./data/teamPages")
        time.sleep(1)

def extractPlayersFromTeamPage():
    for team in teams:
        team_html = read_html(f"data/teamPages/{team.name}.html")
        if not team_html:
            print(f"Skipping {team.name} due to missing file.")
            continue
        
        soup = BeautifulSoup(team_html, 'html.parser')
        rows = soup.select("#stats_standard_9 > tbody > tr")
        
        for row in rows:
            name_tag = row.select_one("th[data-stat='player'] a")
            position_tag = row.select_one("td[data-stat='position']")
            
            if name_tag and position_tag:
                player_name = name_tag.text.strip()
                player_url = "https://fbref.com" + name_tag['href']
                position = position_tag.text.strip()
                
                players.append(Player(player_name, player_url, position, team.name))

def search_players(name=None, position=None, team=None):
    """
    Search players by name, position, or team.
    Parameters:
        name (str): Part or full name of the player.
        position (str): Position code (e.g., 'GK', 'DF', 'MF', 'FW').
        team (str): Part or full name of the team.
    """
    results = []
    for player in players:
        if (name and name.lower() not in player.name.lower()) or \
           (position and position.lower() != player.position.lower()) or \
           (team and team.lower() not in player.team.lower()):
            continue
        results.append(player)

    if results:
        print(f"Found {len(results)} players:")
        for result in results:
            print(result)
    else:
        print("No players found with the specified criteria.")


def main():
    save_html(mainPageURL, 'homepage.html')
    extractURLandNames()
    # saveTeamHTML()
    extractPlayersFromTeamPage()
    # search_players("Haaland", "FW", "Manchester City")

main()
