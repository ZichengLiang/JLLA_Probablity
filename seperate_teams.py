import json
import os

def separate_json_by_team(input_file):
    """
    Separate a JSON file into multiple JSON files, one for each team.
    
    Args:
    input_file (str): Path to the input JSON file containing player data
    
    Returns:
    None: Creates separate JSON files for each team
    """
    # Ensure the output directory exists
    output_dir = 'team_files'
    os.makedirs(output_dir, exist_ok=True)
    
    # Read the entire JSON file
    with open(input_file, 'r') as f:
        players = json.load(f)
    
    # Dictionary to store players by team
    teams = {}
    
    # Organize players by team
    for player in players:
        team = player.get('team', 'Unknown')
        
        # If team not yet in dictionary, create a new list
        if team not in teams:
            teams[team] = []
        
        # Add player to their team's list
        teams[team].append(player)
    
    # Write each team's players to a separate JSON file
    for team, team_players in teams.items():
        # Create a safe filename (replace spaces, remove special characters)
        safe_team_name = ''.join(char for char in team if char.isalnum() or char.isspace()).rstrip()
        safe_team_name = safe_team_name.replace(' ', '_')
        
        output_file = os.path.join(output_dir, f"{safe_team_name}.json")
        
        # Write the team's players to their respective JSON file
        with open(output_file, 'w') as f:
            json.dump(team_players, f, indent=4)
        
        print(f"Created {output_file} with {len(team_players)} players")

# Example usage
if __name__ == "__main__":
    input_file = 'players.json'  # Replace with your input file path
    separate_json_by_team(input_file)