import json, requests, os

# Create the directory structure if it doesn't exist
data_dir = os.path.join(os.path.dirname(__file__), 'data', 'lists')
os.makedirs(data_dir, exist_ok=True)

# File paths for JSON data
STEAM_GAMES_FILE = os.path.join(data_dir, 'steam_games.json')
EPIC_GAMES_FILE = os.path.join(data_dir, 'epic_games.json')
STEAM_ROGUELIKES_FILE = os.path.join(data_dir, 'steam_roguelikes.json')
LAUNCH_OPTIONS_FILE = os.path.join(os.path.dirname(data_dir), 'launch_options.json')

def fetch_steam_games(steam_api_key, steam_id):
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steam_api_key}&steamid={steam_id}&format=json&include_appinfo=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {game['name'].lower(): str(game['appid']) for game in data['response']['games']}
    else:
        print(f"Failed to fetch Steam games. Status code: {response.status_code}")
        return {}

def load_json_data(file_path, default=None):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return default or {}

def save_json_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_launch_options():
    return load_json_data(LAUNCH_OPTIONS_FILE, {})

def update_game_lists(steam_api_key, steam_id):
    # Fetch Steam games
    steam_games = fetch_steam_games(steam_api_key, steam_id)
    
    # Load existing data
    existing_steam_games = load_json_data(STEAM_GAMES_FILE, {})
    epic_games = load_json_data(EPIC_GAMES_FILE, {
        "slime rancher": "corydalis%3A1e38b618d106430db94b474abbfecc16%3ACorydalis",
    })
    steam_roguelikes = load_json_data(STEAM_ROGUELIKES_FILE, {
        "slay the spire": "646570",
        "vampire survivors": "1794680",
        "peglin": "1296610",
        "hades": "1145360",
        "hades 2": "1145350",
    })
    launch_options = load_launch_options()

    # Update Steam games with newly fetched data
    existing_steam_games.update(steam_games)

    # Save updated data
    save_json_data(STEAM_GAMES_FILE, existing_steam_games)
    save_json_data(EPIC_GAMES_FILE, epic_games)
    save_json_data(STEAM_ROGUELIKES_FILE, steam_roguelikes)

    return existing_steam_games, epic_games, steam_roguelikes, launch_options