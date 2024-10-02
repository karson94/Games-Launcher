import os, sys, platform, subprocess, winreg 
from difflib import get_close_matches
from config import STEAM_API_KEY, STEAM_ID
import game_dict

# System-related functions

def get_system_command():
    """
    Determine the appropriate system command to open applications based on the operating system.
    
    :return: The system command as a string ('start' for Windows, 'open' for macOS, 'xdg-open' for Linux)
    """
    system = platform.system()
    if system == "Windows":
        return "start"
    elif system == "Darwin":  # macOS
        return "open"
    elif system == "Linux":
        return "xdg-open"
    else:
        print(f"{system} is an unsupported operating system")
        sys.exit(1)

def get_steam_path():
    """
    Get the default Steam installation path based on the operating system.
    
    :return: The default Steam installation path as a string
    :raises OSError: If the operating system is not supported
    """
    if platform.system() == "Windows":
        return "C:\\Program Files (x86)\\Steam"
    elif platform.system() == "Darwin":  # macOS
        return "~/Library/Application Support/Steam"
    elif platform.system() == "Linux":
        return "~/.local/share/Steam"
    else:
        raise OSError("Unsupported operating system")

def find_java_path():
    """
    Find the Java executable path on Windows systems.
    
    :return: The path to the Java executable if found, None otherwise
    """
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

# Game-related functions

def find_closest_match(game_name):
    """
    Find the closest matching game name from the available games.
    
    :param game_name: The input game name to match
    :return: A list of matching game names
    """
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

def confirm_game_choice(suggested_game, original_input):
    """
    Confirm the game choice with the user if the suggested game differs from the original input.
    
    :param suggested_game: The suggested game name
    :param original_input: The original input from the user
    :return: True if the user confirms, False otherwise
    """
    if suggested_game.lower() != original_input:
        confirm = input(f"Did you mean '{suggested_game.title()}?' (y/n): ").lower()
        return confirm not in ['n', 'no', 'm', 'b', 'h', 'j']
    return True

def handle_multiple_matches(matches, original_input):
    """
    Handle multiple game matches by presenting options to the user.
    
    :param matches: A list of matching game names
    :param original_input: The original input from the user
    :return: The selected game name or None if cancelled
    """
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
    """
    Find the closest matching game and confirm the choice with the user.
    
    :param game_name: The input game name
    :return: The confirmed game name or None if not found or cancelled
    """
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