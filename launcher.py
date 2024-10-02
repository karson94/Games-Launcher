import sys, random, os, platform, subprocess, requests, json
from difflib import get_close_matches
from config import STEAM_API_KEY, STEAM_ID
import game_dict, utils
import shutil, winreg

# Global variables
SYSTEM_COMMAND = None
STEAM_PATH = None
JAVA_PATH = None

# Initialize global variables
def initialize_globals():
    """
    Initialize global variables for system command, Steam path, and Java path.
    Exit the program if any of these cannot be determined.
    """
    global SYSTEM_COMMAND, STEAM_PATH, JAVA_PATH
    SYSTEM_COMMAND = utils.get_system_command()
    STEAM_PATH = utils.get_steam_path()
    JAVA_PATH = utils.find_java_path()

    if not STEAM_PATH:
        print("Error: Unable to determine Steam installation path.")
        sys.exit(1)
    if not JAVA_PATH:
        print("Error: Unable to find Java installation.")
        sys.exit(1)
    if not SYSTEM_COMMAND:
        print("Error: Unable to determine system command.")
        sys.exit(1)

# Game finding and launching functions
def start_game_launch(game_name):
    """
    Start the game launch process by finding and confirming the game, then sending it to the appropriate platform.
    
    :param game_name: The name of the game to launch
    """
    confirmed_game = utils.find_and_confirm_game(game_name)
    if confirmed_game:
        send_to_platform(confirmed_game)

def send_to_platform(game_name):
    """
    Determine the platform (Steam or Epic) for the game and launch it accordingly.
    
    :param game_name: The name of the game to launch
    """
    steam_games = game_dict.load_json_data(game_dict.STEAM_GAMES_FILE, {})
    epic_games = game_dict.load_json_data(game_dict.EPIC_GAMES_FILE, {})

    if game_name in steam_games:
        app_id = steam_games[game_name]
        print(f"Launching {game_name.title()} from Steam...")
        handle_steam_game(app_id)
    elif game_name in epic_games:
        app_id = epic_games[game_name]
        print(f"Launching {game_name.title()} from Epic Games...")
        launch_epic_game(app_id)
    else:
        app_id = game_dict.fetch_steam_game(game_name)
        if app_id:
            steam_games[game_name] = app_id
            game_dict.save_json_data(game_dict.STEAM_GAMES_FILE, steam_games)
            print(f"Launching new Steam game: {game_name.title()}...")
            handle_steam_game(app_id)
        else:
            print(f"Game '{game_name}' not found in the list of known games.")
            list_games("all")

def find_random_roguelike():
    """
    Launch a random roguelike game from the list of Steam roguelikes.
    """
    steam_roguelikes = game_dict.load_json_data(game_dict.STEAM_ROGUELIKES_FILE, {})
    roguelike = random.choice(list(steam_roguelikes.keys()))
    print(f"Launching random roguelike: {roguelike.title()}")
    send_to_platform(roguelike)

# Launch functions
def handle_steam_game(app_id):
    """
    Handle the launching of a Steam game, with special handling for Slay the Spire.
    
    :param app_id: The Steam App ID of the game to launch
    """
    launch_options = game_dict.load_json_data(game_dict.LAUNCH_OPTIONS_FILE, {})
    launch_option = launch_options.get(app_id, '')

    if app_id != '646570':  # Not Slay the Spire's Steam App ID
        launch_steam_game(app_id, launch_option)
    elif app_id == '646570':
        # Special handling for Slay the Spire with Mod the Spire
        sts_path = os.path.join(STEAM_PATH, 'steamapps', 'common', 'SlayTheSpire')
        mts_launcher = os.path.join(sts_path, 'mts-launcher.jar')
        
        if not os.path.exists(mts_launcher):
            print(f"Mod the Spire launcher not found at: {mts_launcher}")
            print("Launching Slay the Spire normally...")
            launch_steam_game(app_id)
        else:
            print("Launching Slay the Spire with Mod the Spire...")
            if not JAVA_PATH:
                print("Java not found. Please make sure Java is installed and added to your PATH.")
                print("Launching Slay the Spire normally...")
                launch_steam_game(app_id)
            else:
                print(f"Java found at: {JAVA_PATH}")
                try:
                    result = subprocess.run([JAVA_PATH, '-version'], capture_output=True, text=True)
                    print(f"Java version: {result.stderr.strip()}")  # Java version is typically printed to stderr
                    
                    print(f"Attempting to run: {JAVA_PATH} -jar {mts_launcher}")
                    
                    # Change the working directory to the Slay the Spire folder
                    original_dir = os.getcwd()
                    os.chdir(sts_path)
                    
                    subprocess.run([JAVA_PATH, '-jar', 'mts-launcher.jar'], check=True)
                    
                    # Change back to the original directory
                    os.chdir(original_dir)
                except subprocess.CalledProcessError as e:
                    print(f"Error occurred while launching Mod the Spire: {e}")
                    print("Launching Slay the Spire normally...")
                    launch_steam_game(app_id)

def launch_epic_game(app_name):
    """
    Launch an Epic game using the appropriate system command.
    
    :param app_name: The Epic Games ID of the game to launch
    """
    if not SYSTEM_COMMAND:
        return

    epic_url = f"com.epicgames.launcher://apps/{app_name}?action=launch&silent=true"
    launch_process(epic_url)

def launch_steam_game(app_id, launch_option=''):
    """
    Launch a Steam game using the appropriate system command.
    
    :param app_id: The Steam App ID of the game to launch
    :param launch_option: Optional launch options for the game
    """
    steam_url = f'steam://rungameid/{app_id}'
    if launch_option:
        steam_url += f'//{launch_option}'
        print(f"Launching game with options: {launch_option}")
    
    launch_process(steam_url)

def launch_process(game_url):
    """
    Launch a game using the appropriate system command.
    
    :param game_url: The URL of the game to launch
    """
    if SYSTEM_COMMAND == "start":
        subprocess.run([SYSTEM_COMMAND, "", game_url], shell=True)
    else:
        subprocess.run([SYSTEM_COMMAND, game_url])

# Utility functions
def list_games(library):
    """
    List all games in the specified library (Steam, Epic, or all).
    
    :param library: The library to list games from ('steam', 'epic', or 'all')
    """
    if library.lower() == 'steam':
        games = game_dict.load_json_data(game_dict.STEAM_GAMES_FILE, {})
    elif library.lower() == 'epic':
        games = game_dict.load_json_data(game_dict.EPIC_GAMES_FILE, {})
    elif library.lower() == 'all':
        games = game_dict.load_json_data(game_dict.STEAM_GAMES_FILE, {})
        games.update(game_dict.load_json_data(game_dict.EPIC_GAMES_FILE, {}))
    else:
        print(f"Unknown library: {library}. Please use 'steam', 'epic', or 'all'.")
        return

    if not games:
        print(f"No games found in the {library.title()} library.")
    else:
        print(f"Games in your {library.title()} library:")
        for game in sorted(games.keys()):
            print(f"- {game.title()}")

# Main execution block
if __name__ == "__main__":
    initialize_globals()
    
    if not STEAM_API_KEY or not STEAM_ID:
        print("Error: STEAM_API_KEY or STEAM_ID not set. Please set them in config.py or personal_config.py")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python game_launcher.py <game_name>")
        print("       python game_launcher.py list <library_name>")
        sys.exit(1)

    if sys.argv[1].lower() == 'list':
        library = sys.argv[2].lower()
        list_games(library)
    elif sys.argv[1].lower() == 'random':
        find_random_roguelike()
    else:
        game_name = " ".join(sys.argv[1:])  # Join all arguments as the game name
        start_game_launch(game_name)