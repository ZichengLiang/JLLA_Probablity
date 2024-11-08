#Place imports below
import requests
from bs4 import BeautifulSoup
import time

# This is the link to the PREMIER LEAGUE page of the FBREF website,
# which we will use to scrape data
mainPageURL = "https://fbref.com/en/comps/9/Premier-League-Stats"
numberTeams = 20
teams = []
"""
parameters{ 
    url : 'the url of the site you wish to save'
    fileName : 'file name to be saved to'
    directory : which folder you wish to save the html. defaultVal = data/
}
"""
def save_html(url, fileName, directory = './data'):
    try:
        pageData = requests.get(url)
        try:
            with open(directory+"/"+fileName, 'wb') as f:
                f.write(pageData.content)
                f.close()
        except:
            print("read error")
    except:
        print("Error: Code 1 - Page Request not valid")
        return;


"""
parameters{
    pathToFile : location where .html file is stored. 
    RETURNS : read data of file / NULL
}
"""
def read_html(pathToFile):
    try:
        with open(pathToFile, 'rb') as f:
            return f.read()
    except:
        return "NULL"


"""
Extracts the urls and team names for teach team and places them into the teamClass with attributes called teams, teamURLS
"""
def extractURLandNames():
    homePage = open("data/homepage.html", "r")
    S = BeautifulSoup(homePage.read(), 'html.parser')
    rows = S.select('#results2024-202591_overall > tbody tr')

    i = 0
    for row in rows:
        teamHREF = row.select("#results2024-202591_overall > tbody > tr:nth-child("+str(i+1)+") > td:nth-child(2) > a")
        beginURL = str(teamHREF[0]).index("/")
        beginURL += 1
        endURL = str(teamHREF[0]).index(">")
        teamURL = str(teamHREF)[beginURL:endURL]
        teamURL = "https://fbref.com"+teamURL

        beginName = endURL + 2
        endName = str(teamHREF[0]).index("</") +1
        teamName = str(teamHREF)[beginName:endName]

        if teamName == ("Nott'ham Forest"):
            teamName = "Nottingham Forest"
        
        i += 1
        teams.append(team(teamName, teamURL))
    
# Team Class:
class team:
    def __init__(self, name, url):
        self.name = name
        self.url = url
    
    def __str__(self):
        return f"{self.name} : {self.url}"

class player:
    def __init__(self, name, url):
        self.name = name
        self.url = url
    
    def __str__(self):
        return f"{self.name} : {self.url}"
    

def saveTeamHTML():
    for team in teams:
        print(team.url)
        print(team.name)
        save_html(team.url, str(team.name)+".html", "./data/teamPages")
        time.sleep(60)

def extractPlayersFromTeamPage():
    for team in teams:
        teamPage = open("data/teamPages/"+team.name+".html", "r")
        S = BeautifulSoup(teamPage.read(), 'html.parser')
        rows = S.select("#stats_standard_9 > tbody tr")
        for row in rows:
            print(row)
            
            
        

def main():
    save_html(mainPageURL, 'homepage.html')
    extractURLandNames()
    # saveTeamHTML()
    extractPlayersFromTeamPage()
    


main()
