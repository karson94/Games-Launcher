import sys, random, os, platform, subprocess, requests, json
from difflib import get_close_matches
from config import STEAM_API_KEY, STEAM_ID
import game_dict
import shutil, winreg

# Global variables
SYSTEM_COMMAND = None
STEAM_PATH = None

# Initialize global variables
def initialize_globals():
    global SYSTEM_COMMAND
    
    # Set system command
    system = platform.system()
    if system == "Windows":
        SYSTEM_COMMAND = "start"
    elif system == "Darwin":  # macOS
        SYSTEM_COMMAND = "open"
    elif system == "Linux":
        SYSTEM_COMMAND = "xdg-open"
    else:
        print(f"{system} is an unsupported operating system")
        sys.exit(1)

def find_java_path():
    try:
        # Try to get Java path from Windows registry
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\Java Runtime Environment")
        version, _ = winreg.QueryValueEx(key, "CurrentVersion")
        key = winreg.OpenKey(key, version)
        path, _ = winreg.QueryValueEx(key, "JavaHome")
        java_exe = os.path.join(path, "bin", "java.exe")
        if os.path.exists(java_exe):
            return java_exe
    except WindowsError:
        pass

    # If registry method fails, try common installation directories
    common_paths = [
        r"C:\Program Files\Java",
        r"C:\Program Files (x86)\Java",
        os.environ.get("JAVA_HOME", "")
    ]

    for path in common_paths:
        for root, dirs, files in os.walk(path):
            if "java.exe" in files:
                return os.path.join(root, "java.exe")

    return None

# Launch a Steam game using the appropriate system command
def launch_steam_game(app_id):
    if not SYSTEM_COMMAND:
        return

    launch_options = game_dict.load_json_data(game_dict.LAUNCH_OPTIONS_FILE, {})
    launch_option = launch_options.get(app_id, '')

    if app_id == '646570':  # Slay the Spire's Steam App ID
        steam_path = get_steam_path()
        sts_path = os.path.join(steam_path, 'steamapps', 'common', 'SlayTheSpire')
        mts_launcher = os.path.join(sts_path, 'mts-launcher.jar')
        
        if os.path.exists(mts_launcher):
            print("Launching Slay the Spire with Mod the Spire...")
            java_path = find_java_path()
            if java_path:
                print(f"Java found at: {java_path}")
                try:
                    result = subprocess.run([java_path, '-version'], capture_output=True, text=True)
                    print(f"Java version: {result.stderr.strip()}")  # Java version is typically printed to stderr
                    
                    print(f"Attempting to run: {java_path} -jar {mts_launcher}")
                    
                    # Change the working directory to the Slay the Spire folder
                    original_dir = os.getcwd()
                    os.chdir(sts_path)
                    
                    subprocess.run([java_path, '-jar', 'mts-launcher.jar'], check=True)
                    
                    # Change back to the original directory
                    os.chdir(original_dir)
                except subprocess.CalledProcessError as e:
                    print(f"Error occurred while launching Mod the Spire: {e}")
                    print("Launching Slay the Spire normally...")
                    launch_steam_url(app_id)
            else:
                print("Java not found. Please make sure Java is installed and added to your PATH.")
                print("Launching Slay the Spire normally...")
                launch_steam_url(app_id)
        else:
            print(f"Mod the Spire launcher not found at: {mts_launcher}")
            print("Launching Slay the Spire normally...")
            launch_steam_url(app_id)
    else:
        launch_steam_url(app_id, launch_option)

def launch_steam_url(app_id, launch_option=''):
    steam_url = f'steam://rungameid/{app_id}'
    if launch_option:
        steam_url += f'//{launch_option}'
        print(f"Launching game with options: {launch_option}")
    else:
        print(f"Launching game")
    
    if SYSTEM_COMMAND == "start":
        subprocess.run([SYSTEM_COMMAND, "", steam_url], shell=True)
    else:
        subprocess.run([SYSTEM_COMMAND, steam_url])

def get_steam_path():
    global STEAM_PATH
    
    if STEAM_PATH is None:
        # This function should return the path to the Steam installation
        # You might need to adjust this based on the user's system
        if platform.system() == "Windows":
            STEAM_PATH = "C:\\Program Files (x86)\\Steam"
        elif platform.system() == "Darwin":  # macOS
            STEAM_PATH = "~/Library/Application Support/Steam"
        elif platform.system() == "Linux":
            STEAM_PATH = "~/.local/share/Steam"
        else:
            raise OSError("Unsupported operating system")
    
    return STEAM_PATH

# Launch an Epic game using the appropriate system command
def launch_epic_game(app_name):
    if not SYSTEM_COMMAND:
        return

    epic_url = f"com.epicgames.launcher://apps/{app_name}?action=launch&silent=true"
    if SYSTEM_COMMAND == "start":
        subprocess.run([SYSTEM_COMMAND, "", epic_url], shell=True)
    else:
        subprocess.run([SYSTEM_COMMAND, epic_url])

# Find the closest matching game name from the available games
def find_closest_match(game_name):
    steam_games = game_dict.load_json_data(game_dict.STEAM_GAMES_FILE, {})
    epic_games = game_dict.load_json_data(game_dict.EPIC_GAMES_FILE, {})
    all_games = list(steam_games.keys()) + list(epic_games.keys())
    
    # Common transformations
    transformations = [
        lambda x: x,  # Original input
        lambda x: x.lower(),  # Lowercase
        lambda x: x.replace(" ", ""),  # Remove spaces
        lambda x: x.replace("2", "ii"),  # Replace 2 with ii
        lambda x: x.replace("3", "iii"),  # Replace 3 with iii
        lambda x: x.replace("4", "iv"),  # Replace 4 with iv
        lambda x: x.replace("5", "v"),  # Replace 5 with v
        lambda x: x.replace("6", "vi"),  # Replace 6 with vi
        lambda x: x.replace("7", "vii"),  # Replace 7 with vii
        lambda x: x.replace("8", "viii"),  # Replace 8 with viii
        lambda x: x.replace("9", "ix"),  # Replace 9 with ix
        lambda x: x.replace("10", "x"),  # Replace 10 with x
    ]
    
    # Common game name aliases
    aliases = {
        "tf2": "team fortress 2",
        "csgo": "counter-strike: global offensive",
        "gta5": "grand theft auto v",
        "gtav": "grand theft auto v",
        "pubg": "playerunknown's battlegrounds",
        "dota": "dota 2",
        "lol": "league of legends",
        "wow": "world of warcraft",
        "r6": "tom clancy's rainbow six siege",
        "r6s": "tom clancy's rainbow six siege",
        "sts": "slay the spire",
    }
    
    # Check for exact matches first (case-insensitive)
    for game in all_games:
        if game_name.lower() == game.lower():
            return [game]
    
    # Check aliases
    if game_name.lower() in aliases:
        alias_match = aliases[game_name.lower()]
        if alias_match in all_games:
            return [alias_match]
    
    # Apply transformations and check for matches
    for transform in transformations:
        transformed_name = transform(game_name)
        partial_matches = [game for game in all_games if transformed_name.lower() in game.lower()]
        if partial_matches:
            return partial_matches
    
    # If no matches found, use get_close_matches for fuzzy matching
    return get_close_matches(game_name.lower(), all_games, n=3, cutoff=0.6)

# Confirm game choice
def confirm_game_choice(suggested_game, original_input):
    if suggested_game.lower() != original_input:
        confirm = input(f"Did you mean '{suggested_game}'? (y/n): ").lower()
        return confirm not in ['n', 'no', 'm', 'b', 'h', 'j']
    return True

# Handle multiple matches
def handle_multiple_matches(matches, original_input):
    print(f"Multiple matches found for '{original_input}':")
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match}")
    choice = input("Enter the number of the game you want to launch (or 'c' to cancel): ")
    if choice.lower() == 'c':
        print("Launch cancelled.")
        return None
    try:
        return matches[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid choice. Cancelling launch.")
        return None

# Find and confirm game
def find_and_confirm_game(game_name):
    original_input = game_name.lower()
    matches = find_closest_match(original_input)
    
    if len(matches) == 1:
        game_name = matches[0]
        if not confirm_game_choice(game_name, original_input):
            return None
    elif len(matches) > 1:
        game_name = handle_multiple_matches(matches, original_input)
        if game_name is None:
            return None
    else:
        print(f"No matches found for '{original_input}'.")
        print_all_games()
        return None
    
    return game_name

# Launch game by platform
def launch_game_by_platform(game_name):
    steam_games = game_dict.load_json_data(game_dict.STEAM_GAMES_FILE, {})
    epic_games = game_dict.load_json_data(game_dict.EPIC_GAMES_FILE, {})

    if game_name in steam_games:
        app_id = steam_games[game_name]
        print(f"Launching {game_name.title()} from Steam...")
        launch_steam_game(app_id)
    elif game_name in epic_games:
        app_id = epic_games[game_name]
        print(f"Launching {game_name.title()} from Epic Games...")
        launch_epic_game(app_id)
    else:
        app_id = fetch_steam_game(game_name)
        if app_id:
            steam_games[game_name] = app_id
            game_dict.save_json_data(game_dict.STEAM_GAMES_FILE, steam_games)
            print(f"Launching new Steam game: {game_name.title()}...")
            launch_steam_game(app_id)
        else:
            print(f"Game '{game_name}' not found in the list of known games.")
            print_all_games()

# Main function to launch a game
def launch_game(game_name):
    confirmed_game = find_and_confirm_game(game_name)
    if confirmed_game:
        launch_game_by_platform(confirmed_game)

# Launch a random roguelike game
def launch_random_roguelike():
    steam_roguelikes = game_dict.load_json_data(game_dict.STEAM_ROGUELIKES_FILE, {})
    roguelike = random.choice(list(steam_roguelikes.keys()))
    print(f"Launching random roguelike: {roguelike.title()}")
    launch_game(roguelike)

# New function to list games from a specific library
def list_games(library):
    if library.lower() == 'steam':
        games = game_dict.load_json_data(game_dict.STEAM_GAMES_FILE, {})
    elif library.lower() == 'epic':
        games = game_dict.load_json_data(game_dict.EPIC_GAMES_FILE, {})
    else:
        print(f"Unknown library: {library}. Please use 'steam' or 'epic'.")
        return

    if not games:
        print(f"No games found in the {library.capitalize()} library.")
    else:
        print(f"Games in your {library.capitalize()} library:")
        for game in sorted(games.keys()):
            print(f"- {game.title()}")

# Add this check:
if not STEAM_API_KEY or not STEAM_ID:
    print("Error: STEAM_API_KEY or STEAM_ID not set. Please set them in config.py or personal_config.py")
    sys.exit(1)

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

    if sys.argv[1].lower() in ['list steam', 'list epic']:
        library = sys.argv[1][5:]
        list_games(library)
    else:
        game_name = " ".join(sys.argv[1:])  # Join all arguments as the game name
        launch_game(game_name)