import os
import requests
from bs4 import BeautifulSoup
import time
import sys
import json

mainPageURL = "https://fbref.com/en/comps/9/Premier-League-Stats"
numberTeams = 20
teams = []
players = []

#This is just a fun function: Delete if performance heavy and uncomment the last line in addstatstoplayers
def display_loading_bar(count, total, bar_length=40):
    """
    Displays a loading bar in the terminal.
    Parameters:
        count (int): Current progress count.
        total (int): Total count for completion.
        bar_length (int): Length of the loading bar in characters.
    """
    progress = count / total
    block = int(round(bar_length * progress))
    bar = "#" * block + "-" * (bar_length - block)
    sys.stdout.write(f"\r[{bar}] {progress * 100:.2f}%\n")
    sys.stdout.flush()


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
        self.isGoalkeeper = (position == "GK")

        #Common stats:
        self.matchesPlayed = 0
        self.starts = 0

        # GK STATS:
        self.savePercentage = 0

        # Outfielder Stats:
        self.tacklesPG = 0
        self.interceptionsPG = 0
        self.shotsPG = 0
        self.passesPG = 0
        self.progPassesRecievedPG = 0
        self.progCarriesPG = 0
    
    def __str__(self):
        return f"[Name: {self.name}\n URL: {self.url}\n POS: {self.position}\n Team: {self.team}\n SavePercentage(Keepers Only): {self.savePercentage}\n TacklesPG: {self.tacklesPG}\n InterceptionsPG: {self.interceptionsPG}\n ShotsPG: {self.shotsPG}\n PassesPG: {self.passesPG}\n ProgPassesRec: {self.progPassesRecievedPG}\n ProgCarries: {self.progCarriesPG}]"
    

    def setGKStats(self, savePercentage, matchesPlayed, starts, startsForCurrentTeam):
        self.matchesPlayed = matchesPlayed
        self.savePercentage = savePercentage
        self.starts = starts
        self.startsForCurrentTeam = startsForCurrentTeam
    
    def setOutfielderStats(self, tackles, passes, shots, interceptions, 
                           progPassRecieved, progCarries, matchesPlayed, starts, startsForCurrentTeam):
        #The values come in as player career totals. We divide by player games played to get per game stats.
        self.tacklesPG = tackles/matchesPlayed
        self.passesPG = passes/matchesPlayed
        self.shotsPG = shots/matchesPlayed
        self.interceptionsPG = interceptions/matchesPlayed
        self.progPassesRecievedPG = progPassRecieved/matchesPlayed
        self.progCarriesPG = progCarries/matchesPlayed
        self.matchesPlayed = matchesPlayed
        self.starts = starts
        self.startsForCurrentTeam = startsForCurrentTeam
    
    def to_dict(self):
        return {
            "name": self.name,
            "url": self.url,
            "position": self.position,
            "team": self.team,
            "isGoalkeeper": self.isGoalkeeper,
            "matchesPlayed": self.matchesPlayed,
            "savePercentage": self.savePercentage,
            "tacklesPG": self.tacklesPG,
            "interceptionsPG": self.interceptionsPG,
            "shotsPG": self.shotsPG,
            "passesPG": self.passesPG,
            "progPassesRecievedPG": self.progPassesRecievedPG,
            "progCarriesPG": self.progCarriesPG,
            "starts" : self.starts,
            "startsForCurrentTeam" : self.startsForCurrentTeam
        }

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
        return results
    else:
        print("No players found with the specified criteria.")

def savePlayersStatsHTML(players):
    for player in players:
        if player.isGoalkeeper:
            save_html(player.url, f"{player.name}.html", "./data/players/keeperPages")
        else:
            save_html(player.url, f"{player.name}.html", "./data/players/outfielderPages")

        time.sleep(15)

def addStatsToPlayer():
    count = 0
    for player in players:
        try:
            if player.isGoalkeeper:
                player_html = read_html(f"./data/players/keeperPages/{player.name}.html")
                if not player_html:
                    print(f"Skipping {player.name}, as HTML read was invalid.")
                    continue
                soup = BeautifulSoup(player_html, "html.parser")

                if soup is None:
                    print(f"{player.name} does not have necessary values.")
                    continue

                savesPerGame = 0
                keeperMatchesPlayed = 0
                starts = 0
                startsForCurrentTeam = 0
                try:
                    keeperMatchesPlayed = int(soup.select("#stats_keeper_dom_lg > tfoot > tr:nth-child(1) > td:nth-child(6)")[0].get_text(strip=True)or 0)
                    savesPerGame = float(soup.select("#stats_keeper_dom_lg > tfoot > tr:nth-child(1) > td:nth-child(14)")[0].get_text(strip=True)or 0)
                    starts = float(soup.select("#stats_keeper_dom_lg > tfoot > tr:nth-child(1) > td:nth-child(7)")[0].get_text(strip=True)or 0)

                    gTable = soup.select("#stats_keeper_dom_lg > tbody")
                    print(gTable)

                    player.setGKStats(savesPerGame, keeperMatchesPlayed, starts)
                    print(f"Updated stats for {player.name}\n")
                except Exception as e:
                    print(f"Unexpected error processing {player.name}: {e}")

            else:
                player_html = read_html(f"./data/players/outfielderPages/{player.name}.html")
                if not player_html:
                    print(f"Skipping {player.name}, as HTML read was invalid.")
                    continue
                
                soup = BeautifulSoup(player_html, "html.parser")
                
                if soup is None:
                    print(f"{player.name} does not have necessary values.")
                    continue
                
                # Initialize variables with defaults
                matchesPlayed = 0
                tackles = 0
                interceptions = 0
                shots = 0
                passes = 0#stats_standard_dom_lg > tfoot > tr:nth-child(1) > 
                progPassesRecieved = 0
                progCarries = 0
                starts = 0
                startsForCurrentTeam = 0
                
                # Parse stats using row.select() and assign values
                try:
                    matchesPlayed = int(soup.select("#stats_standard_dom_lg > tfoot > tr:nth-child(1) > td:nth-child(6)")[0].get_text(strip=True)or 0)
                    tackles = float(soup.select("#stats_defense_dom_lg > tfoot > tr:nth-child(1) > td:nth-child(7)")[0].get_text(strip=True) or 0)
                    interceptions = float(soup.select("#stats_defense_dom_lg > tfoot > tr:nth-child(1) > td:nth-child(19)")[0].get_text(strip=True) or 0)
                    shots = float(soup.select("#stats_shooting_dom_lg > tfoot > tr:nth-child(1) > td:nth-child(7)")[0].get_text(strip=True) or 0)
                    passes = float(soup.select("#stats_passing_dom_lg > tfoot > tr:nth-child(1) > td:nth-child(8)")[0].get_text(strip=True) or 0)
                    progPassesRecieved = float(soup.select("#stats_possession_dom_lg > tfoot > tr:nth-child(1) > td:nth-child(28)")[0].get_text(strip=True) or 0)
                    progCarries = float(soup.select("#stats_possession_dom_lg > tfoot > tr:nth-child(1) > td:nth-child(19)")[0].get_text(strip=True) or 0)
                    starts = float(soup.select("#stats_standard_dom_lg > tfoot > tr:nth-child(1) > td:nth-child(7)")[0].get_text(strip=True) or 0)

                    gTable = soup.select("#stats_standard_dom_lg > tbody")
                    print(gTable)
                    
                    player.setOutfielderStats(tackles, passes, shots, interceptions, progPassesRecieved, progCarries, matchesPlayed, starts, startsForCurrentTeam)
                    print(f"Updated stats for {player.name}\n")
                except Exception as e:
                    print(f"Error extracting stats for {player.name}: {e}")
                    continue
        
        except Exception as e:
            print(f"Unexpected error processing {player.name}: {e}")
        
        count += 1
        display_loading_bar(count, len(players))
        #print(f"Percentage Complete: {(count/len(players))*100:.2f}%")



def players_to_json(players):
    players_dict_list = [player.to_dict() for player in players]
    return json.dumps(players_dict_list, indent=4) 

def save_players_to_json_file(players, filename="players.json"):
    players_json = players_to_json(players)
    with open(filename, "w") as f:
        f.write(players_json)

            

def main():
    save_html(mainPageURL, 'homepage.html')
    extractURLandNames()
    # saveTeamHTML()
    extractPlayersFromTeamPage()
    #savePlayersStatsHTML()
    addStatsToPlayer()

    #save_players_to_json_file(players)

main()
