import json, requests, os

class GameManager:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data', 'lists')
        os.makedirs(self.data_dir, exist_ok=True)
        self.steam_games_file = os.path.join(self.data_dir, 'steam_games.json')
        self.epic_games_file = os.path.join(self.data_dir, 'epic_games.json')
        self.steam_roguelikes_file = os.path.join(self.data_dir, 'steam_roguelikes.json')
        self.launch_options_file = os.path.join(os.path.dirname(self.data_dir), 'launch_options.json')
        self.initialize_json_files()

    def initialize_json_files(self):
        required_files = {
            self.steam_games_file: {},
            self.epic_games_file: {},
            self.steam_roguelikes_file: {},
            self.launch_options_file: {}
        }
        for file_path, default_data in required_files.items():
            if not os.path.exists(file_path):
                print(f"Creating {os.path.basename(file_path)}...")
                self.save_json_data(file_path, default_data)

    def fetch_steam_games(self, steam_api_key, steam_id):
        url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steam_api_key}&steamid={steam_id}&format=json&include_appinfo=1"
        response = requests.get(url)
        print(f"Steam API status code: {response.status_code}")  # Debug
        print(f"Raw response text: {response.text}")  # Debug
        try:
            data = response.json()
            print(f"Parsed data: {data}")  # Debug
        except Exception as e:
            print(f"Failed to parse JSON: {e}")
            return {}
        if response.status_code == 200:
            return {game['name'].lower(): str(game['appid']) for game in data.get('response', {}).get('games', [])}
        else:
            print(f"Failed to fetch Steam games. Status code: {response.status_code}")
            return {}

    def load_json_data(self, file_path, default=None, allow_update=True):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            if allow_update and file_path == self.steam_games_file and (not os.path.exists(file_path) or os.path.getsize(file_path) == 0 or open(file_path, 'r').read().strip() == '{}'):
                print("[DEBUG] Triggering Steam games fetch in load_json_data...")
                from config import STEAM_API_KEY, STEAM_ID
                steam_games = self.fetch_steam_games(STEAM_API_KEY, STEAM_ID)
                self.save_json_data(self.steam_games_file, steam_games)
                return steam_games
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                print(f"[DEBUG] Returning data from file: {file_path}")
                with open(file_path, 'r') as f:
                    return json.load(f)
            print(f"[DEBUG] Creating file with default data: {file_path}")
            default = default or {}
            self.save_json_data(file_path, default)
            return default
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"[DEBUG] Exception caught, recreating file: {file_path}")
            default = default or {}
            self.save_json_data(file_path, default)
            return default

    def save_json_data(self, file_path, data):
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_launch_options(self):
        return self.load_json_data(self.launch_options_file, {})

    def update_game_lists(self, steam_api_key, steam_id):
        steam_games = self.fetch_steam_games(steam_api_key, steam_id)
        existing_steam_games = self.load_json_data(self.steam_games_file, {}, allow_update=False)
        epic_games = self.load_json_data(self.epic_games_file, {}, allow_update=False)
        steam_roguelikes = self.load_json_data(self.steam_roguelikes_file, {}, allow_update=False)
        launch_options = self.load_launch_options()
        existing_steam_games.update(steam_games)
        self.save_json_data(self.steam_games_file, existing_steam_games)
        self.save_json_data(self.epic_games_file, epic_games)
        self.save_json_data(self.steam_roguelikes_file, steam_roguelikes)
        return existing_steam_games, epic_games, steam_roguelikes, launch_options

# Initialize the GameManager
game_manager = GameManager()