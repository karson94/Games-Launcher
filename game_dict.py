import json, requests, os

# Create the directory structure if it doesn't exist
data_dir = os.path.join(os.path.dirname(__file__), 'data', 'lists')
os.makedirs(data_dir, exist_ok=True)

# File paths for JSON data
STEAM_GAMES_FILE = os.path.join(data_dir, 'steam_games.json')
EPIC_GAMES_FILE = os.path.join(data_dir, 'epic_games.json')
STEAM_ROGUELIKES_FILE = os.path.join(data_dir, 'steam_roguelikes.json')
LAUNCH_OPTIONS_FILE = os.path.join(os.path.dirname(data_dir), 'launch_options.json')

def initialize_json_files():
    """
    Create all necessary JSON files if they don't exist.
    """
    required_files = {
        STEAM_GAMES_FILE: {},
        EPIC_GAMES_FILE: {},
        STEAM_ROGUELIKES_FILE: {},
        LAUNCH_OPTIONS_FILE: {}
    }

    for file_path, default_data in required_files.items():
        if not os.path.exists(file_path):
            print(f"Creating {os.path.basename(file_path)}...")
            save_json_data(file_path, default_data)

# Initialize the files
initialize_json_files()

def fetch_steam_games(steam_api_key, steam_id):
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steam_api_key}&steamid={steam_id}&format=json&include_appinfo=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {game['name'].lower(): str(game['appid']) for game in data['response']['games']}
    else:
        print(f"Failed to fetch Steam games. Status code: {response.status_code}")
        return {}

def load_json_data(file_path, default=None, allow_update=True):
    """
    Load JSON data from a file, updating game lists if necessary.
    
    :param file_path: Path to the JSON file
    :param default: Default data to use if file doesn't exist
    :param allow_update: Whether to allow updating game lists (to prevent recursion)
    :return: Loaded data or default value
    """
    try:
        # Make sure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # If loading Steam games file and it's empty/invalid, update all game lists
        if allow_update and file_path == STEAM_GAMES_FILE and (not os.path.exists(file_path) or os.path.getsize(file_path) == 0):
            print("Updating game lists...")
            from config import STEAM_API_KEY, STEAM_ID
            steam_games, _, _, _ = update_game_lists(STEAM_API_KEY, STEAM_ID)
            return steam_games
            
        # Try to read the file
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r') as f:
                return json.load(f)
                
        # File doesn't exist or is empty, create it with default data
        default = default or {}
        save_json_data(file_path, default)
        return default
            
    except (FileNotFoundError, json.JSONDecodeError):
        default = default or {}
        save_json_data(file_path, default)
        return default

def save_json_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_launch_options():
    return load_json_data(LAUNCH_OPTIONS_FILE, {})

def update_game_lists(steam_api_key, steam_id):
    # Fetch Steam games
    steam_games = fetch_steam_games(steam_api_key, steam_id)
    
    # Load existing data
    existing_steam_games = load_json_data(STEAM_GAMES_FILE, {}, allow_update=False)
    epic_games = load_json_data(EPIC_GAMES_FILE, {}, allow_update=False)
    steam_roguelikes = load_json_data(STEAM_ROGUELIKES_FILE, {}, allow_update=False)
    launch_options = load_launch_options()

    # Update Steam games with newly fetched data
    existing_steam_games.update(steam_games)

    # Save updated data
    save_json_data(STEAM_GAMES_FILE, existing_steam_games)
    save_json_data(EPIC_GAMES_FILE, epic_games)
    save_json_data(STEAM_ROGUELIKES_FILE, steam_roguelikes)

    return existing_steam_games, epic_games, steam_roguelikes, launch_options