import sys, random, os, platform, subprocess, requests, json
from difflib import get_close_matches
from config import STEAM_API_KEY, STEAM_ID
from game_dict import game_manager
import shutil, winreg
from utils import get_logger, add_alias, find_and_confirm_game, find_closest_match, get_aliases, remove_alias, find_game_with_alias

logger = get_logger(__name__)

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
    SYSTEM_COMMAND = get_system_command()
    STEAM_PATH = get_steam_path()
    JAVA_PATH = find_java_path()

    if not STEAM_PATH:
        logger.error("Error: Unable to determine Steam installation path.")
        sys.exit(1)
    if not JAVA_PATH:
        logger.error("Error: Unable to find Java installation.")
        sys.exit(1)
    if not SYSTEM_COMMAND:
        logger.error("Error: Unable to determine system command.")
        sys.exit(1)

# System-related functions

def get_system_command():
    system = platform.system()
    if system == "Windows":
        return "start"
    elif system == "Darwin":
        return "open"
    elif system == "Linux":
        return "xdg-open"
    else:
        print(f"{system} is an unsupported operating system")
        sys.exit(1)

def get_steam_path():
    if platform.system() == "Windows":
        return "C:\\Program Files (x86)\\Steam"
    elif platform.system() == "Darwin":
        return "~/Library/Application Support/Steam"
    elif platform.system() == "Linux":
        return "~/.local/share/Steam"
    else:
        raise OSError("Unsupported operating system")

def find_java_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\Java Runtime Environment")
        version, _ = winreg.QueryValueEx(key, "CurrentVersion")
        key = winreg.OpenKey(key, version)
        path, _ = winreg.QueryValueEx(key, "JavaHome")
        java_exe = os.path.join(path, "bin", "java.exe")
        if os.path.exists(java_exe):
            return java_exe
    except WindowsError:
        pass

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

# Game-related functions

def normalize_game_name(game_name):
    transformations = [
        lambda x: x.lower(),
        lambda x: x.replace(" ", ""),
        lambda x: x.replace("2", "ii"),
        lambda x: x.replace("3", "iii"),
        lambda x: x.replace("4", "iv"),
        lambda x: x.replace("5", "v"),
        lambda x: x.replace("6", "vi"),
        lambda x: x.replace("7", "vii"),
        lambda x: x.replace("8", "viii"),
        lambda x: x.replace("9", "ix"),
        lambda x: x.replace("10", "x"),
    ]
    return [transform(game_name) for transform in transformations]

def format_game_title(game_name):
    roman_to_num = {
        'ii': '2', 'iii': '3', 'iv': '4', 'v': '5',
        'vi': '6', 'vii': '7', 'viii': '8', 'ix': '9', 'x': '10'
    }
    words = game_name.split()
    for i, word in enumerate(words):
        word_lower = word.lower()
        for roman, num in roman_to_num.items():
            if word_lower == roman:
                words[i] = num
                break
        else:
            if "'" in word:
                parts = word.split("'")
                words[i] = parts[0].capitalize() + "'" + parts[1]
            else:
                words[i] = word.capitalize()
    return " ".join(words)

def confirm_game_choice(suggested_game, original_input):
    if suggested_game.lower() != original_input:
        confirm = input(f"Did you mean '{suggested_game.title()}?' (y/n): ").lower()
        return confirm not in ['n', 'no', 'm', 'b', 'h', 'j']
    return True

def handle_multiple_matches(matches, original_input):
    print(f"Multiple matches found for '{original_input}':")
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match.title()}")
    choice = input("Enter the number of the game you want to launch (or 'c' to cancel): ")
    if choice.lower() == 'c':
        print("Launch cancelled.")
        return None
    try:
        return matches[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid choice. Cancelling launch.")
        return None

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

def print_all_games():
    steam_games = game_manager.load_json_data(game_manager.steam_games_file, {})
    epic_games = game_manager.load_json_data(game_manager.epic_games_file, {})
    all_games = sorted(list(steam_games.keys()) + list(epic_games.keys()))
    print("\nAvailable games:")
    for game in all_games:
        print(f"- {game.title()}")

def launch_steam_game(game_name):
    steam_games = game_manager.load_json_data(game_manager.steam_games_file, {})
    if game_name.lower() in steam_games:
        app_id = steam_games[game_name.lower()]
        steam_path = get_steam_path()
        steam_exe = os.path.join(steam_path, "Steam.exe")
        if os.path.exists(steam_exe):
            subprocess.Popen([steam_exe, f"steam://rungameid/{app_id}"])
            print(f"Launching {game_name.title()}...")
        else:
            logger.error("Steam executable not found.")
    else:
        logger.error(f"Game '{game_name}' not found in Steam library.")

def launch_epic_game(game_name):
    epic_games = game_manager.load_json_data(game_manager.epic_games_file, {})
    if game_name.lower() in epic_games:
        epic_path = epic_games[game_name.lower()]
        if os.path.exists(epic_path):
            subprocess.Popen([epic_path])
            print(f"Launching {game_name.title()}...")
        else:
            logger.error(f"Game executable not found at {epic_path}")
    else:
        logger.error(f"Game '{game_name}' not found in Epic library.")

def launch_game(game_name):
    game_name = find_and_confirm_game(game_name)
    if game_name:
        steam_games = game_manager.load_json_data(game_manager.steam_games_file, {})
        epic_games = game_manager.load_json_data(game_manager.epic_games_file, {})
        if game_name.lower() in steam_games:
            launch_steam_game(game_name)
        elif game_name.lower() in epic_games:
            launch_epic_game(game_name)
        else:
            logger.error(f"Game '{game_name}' not found in any library.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python launcher.py [list|launch|alias] [steam|epic|game_name|alias] [shortcut]")
        print("Alias usage:")
        print("  python launcher.py alias list [game]")
        print("  python launcher.py alias add <game> <shortcut>")
        sys.exit(1)

    command = sys.argv[1].lower()
    if command == "list":
        if len(sys.argv) < 3:
            print("Usage: python launcher.py list [steam|epic]")
            sys.exit(1)
        platform = sys.argv[2].lower()
        if platform == "steam":
            steam_games = game_manager.load_json_data(game_manager.steam_games_file, {})
            print("\nSteam games:")
            for game in sorted(steam_games.keys()):
                print(f"- {game.title()}")
        elif platform == "epic":
            epic_games = game_manager.load_json_data(game_manager.epic_games_file, {})
            print("\nEpic games:")
            for game in sorted(epic_games.keys()):
                print(f"- {game.title()}")
        else:
            logger.error("Invalid platform. Use 'steam' or 'epic'.")
        return
    elif command == "alias":
        if len(sys.argv) < 3:
            print("Alias usage:")
            print("  python launcher.py alias list [game]")
            print("  python launcher.py alias add <game> <shortcut>")
            sys.exit(1)
        alias_cmd = sys.argv[2].lower()
        if alias_cmd == "list":
            aliases = get_aliases()
            if len(sys.argv) == 3:
                # List all aliases
                if not aliases:
                    print("No aliases found.")
                else:
                    print("Aliases:")
                    for game, alias_list in aliases.items():
                        print(f"{game}: {', '.join(alias_list) if alias_list else '(none)'}")
            else:
                # List aliases for a specific game (with fuzzy/alias matching)
                input_name = " ".join(sys.argv[3:])
                resolved_game = find_and_confirm_game(input_name)
                if not resolved_game:
                    print(f"Could not find a game matching '{input_name}'.")
                    sys.exit(1)
                alias_list = aliases.get(resolved_game.lower(), [])
                print(f"Aliases for '{resolved_game}': {', '.join(alias_list) if alias_list else '(none)'}")
            return
        elif alias_cmd == "add":
            if len(sys.argv) < 5:
                print("Usage: python launcher.py alias add <game> <shortcut>")
                sys.exit(1)
            input_name = sys.argv[3]
            shortcut = sys.argv[4]
            resolved_game = find_and_confirm_game(input_name)
            if not resolved_game:
                print(f"Could not find a game matching '{input_name}'.")
                sys.exit(1)
            result = add_alias(resolved_game, shortcut)
            if result is True:
                print(f"Added alias '{shortcut}' for game '{resolved_game}'.")
            elif result is False:
                print(f"Alias '{shortcut}' already exists for game '{resolved_game}'.")
            else:
                # result is the conflicting game
                print(f"Alias '{shortcut}' already exists for game '{result}'.")
                confirm = input(f"Do you want to remove alias '{shortcut}' from '{result}' and add it to '{resolved_game}'? (y/n): ").strip().lower()
                if confirm == 'y':
                    remove_alias(result, shortcut)
                    add_alias(resolved_game, shortcut)
                    print(f"Alias '{shortcut}' moved from '{result}' to '{resolved_game}'.")
                else:
                    print("Action cancelled. Alias not added.")
            return
        elif alias_cmd == "remove":
            if len(sys.argv) < 5:
                print("Usage: python launcher.py alias remove <game> <shortcut>")
                sys.exit(1)
            input_name = sys.argv[3]
            shortcut = sys.argv[4]
            resolved_game = find_and_confirm_game(input_name)
            if not resolved_game:
                print(f"Could not find a game matching '{input_name}'.")
                sys.exit(1)
            if remove_alias(resolved_game, shortcut):
                print(f"Removed alias '{shortcut}' from game '{resolved_game}'.")
            else:
                print(f"Alias '{shortcut}' not found for game '{resolved_game}'.")
            return
        else:
            print("Unknown alias subcommand. Use 'list', 'add', or 'remove'.")
            sys.exit(1)
    elif command == "launch":
        if len(sys.argv) < 3:
            print("Usage: python launcher.py launch [game_name]")
            sys.exit(1)
        game_name = " ".join(sys.argv[2:])
        launch_game(game_name)
    else:
        # If command n/a, launch game
        game_name = " ".join(sys.argv[1:])
        launch_game(game_name)

if __name__ == "__main__":
    initialize_globals()
    
    if not STEAM_API_KEY or not STEAM_ID:
        logger.error("Error: STEAM_API_KEY or STEAM_ID not set. Please set them in config.py or personal_config.py")
        sys.exit(1)

    main()
