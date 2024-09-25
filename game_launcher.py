import sys
import random
import os
import platform
import subprocess
from game_dict import STEAM_GAME_DICT, STEAM_ROUGLIKES, EPIC_GAME_DICT
from difflib import get_close_matches

def find_closest_match(game_name):
    return get_close_matches(game_name.lower(), STEAM_GAME_DICT.keys(), n=2, cutoff=0.65)

def print_all_games():
    print("Available games:")
    for game in sorted(STEAM_GAME_DICT.keys()):
        print(f"- {game}")

def launch_random_roguelike():
    roguelike = random.choice(list(STEAM_ROUGLIKES.keys()))
    print(f"Launching random roguelike: {roguelike}")
    launch_game(roguelike)

def launch_game(game_name):
    game_name = game_name.lower()
    if game_name == "roguelikes":
        launch_random_roguelike()
    elif game_name in STEAM_GAME_DICT:
        app_id = STEAM_GAME_DICT[game_name]
        print(f"Launching {game_name} from Steam...")
        launch_steam_game(app_id)
    elif game_name in EPIC_GAME_DICT:
        app_name = EPIC_GAME_DICT[game_name]
        print(f"Launching {game_name} from Epic Games...")
        launch_epic_game(app_name)
    else:
        closest_match = find_closest_match(game_name)
        if closest_match:
            print(f"Game '{game_name}' not found. Did you mean '{closest_match[0]}'?")
            user_input = input("Press Enter to launch this game, or type 'n' to cancel: ").lower()
            if user_input != 'n':
                launch_game(closest_match[0])
        else:
            print(f"Game '{game_name}' not found in the list of known games.")
            print_all_games()

def launch_steam_game(app_id):
    system = platform.system()
    if system == "Windows":
        os.system(f'start steam://rungameid/{app_id}')
    elif system == "Darwin":  # macOS
        os.system(f'open steam://rungameid/{app_id}')
    elif system == "Linux":
        os.system(f'xdg-open steam://rungameid/{app_id}')
    else:
        print(f"Unsupported operating system: {system}")

def launch_epic_game(app_name):
    system = platform.system()
    if system == "Windows":
        epic_launcher = r"C:\Program Files (x86)\Epic Games\Launcher\Portal\Binaries\Win32\EpicGamesLauncher.exe"
        subprocess.Popen([epic_launcher, "-com.epicgames.launcher://apps/" + app_name + "?action=launch", "&silent"])
    elif system == "Darwin":  # macOS
        epic_launcher = "/Applications/Epic Games Launcher.app/Contents/MacOS/EpicGamesLauncher"
        subprocess.Popen([epic_launcher, "-com.epicgames.launcher://apps/" + app_name + "?action=launch", "&silent"])
    else:
        print(f"Epic Games Launcher is not supported on {system}")

def list_epic_games():
    try:
        result = subprocess.run(["powershell", "-Command", "& {Get-ItemProperty 'HKLM:\\SOFTWARE\\WOW6432Node\\Epic Games\\EpicGamesLauncher\\AppDataPath'}"], capture_output=True, text=True)
        epic_path = result.stdout.strip()
        
        with open(f"{epic_path}\\Manifests\\*.item", "r") as f:
            for line in f:
                game_info = json.loads(line)
                print(f"Game: {game_info['DisplayName']}, ID: {game_info['AppName']}")
    except Exception as e:
        print(f"Error listing Epic Games: {e}")

# Call this function to see all installed Epic Games and their IDs
list_epic_games()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python game_launcher.py <game_name>")
        sys.exit(1)

    game_name = " ".join(sys.argv[1:])  # Join all arguments as the game name
    launch_game(game_name)