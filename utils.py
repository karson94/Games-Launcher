import os, sys, platform, subprocess, winreg 
from difflib import get_close_matches
from config import STEAM_API_KEY, STEAM_ID
import game_dict
import json
import logging

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if not logger.hasHandlers():
        file_handler = logging.FileHandler('gameslauncher.log')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    return logger

# Aliases/shortcuts management
ALIAS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'alias.json')

def load_aliases():
    if not os.path.exists(ALIAS_FILE):
        return {}
    with open(ALIAS_FILE, 'r') as f:
        return json.load(f)

def save_aliases(aliases):
    os.makedirs(os.path.dirname(ALIAS_FILE), exist_ok=True)
    with open(ALIAS_FILE, 'w') as f:
        json.dump(aliases, f, indent=2)

def get_aliases():
    return load_aliases()

def find_game_with_alias(alias):
    aliases = load_aliases()
    alias = alias.lower()
    for game, alias_list in aliases.items():
        if alias in [a.lower() for a in alias_list]:
            return game
    return None

def add_alias(game_name, alias):
    aliases = load_aliases()
    game_key = game_name.lower()
    alias = alias.lower()
    # Check if alias exists for another game
    for g, alias_list in aliases.items():
        if alias in [a.lower() for a in alias_list]:
            if g != game_key:
                return g  # Conflict: alias exists for another game
            else:
                return False  # Already exists for this game
    if game_key not in aliases:
        aliases[game_key] = []
    if alias not in aliases[game_key]:
        aliases[game_key].append(alias)
        save_aliases(aliases)
        return True
    return False

def get_game_for_alias(input_name):
    aliases = load_aliases()
    for game, alias_list in aliases.items():
        if input_name.lower() == game.lower() or input_name.lower() in [a.lower() for a in alias_list]:
            return game
    return None

def remove_alias(game_name, alias):
    aliases = load_aliases()
    game_key = game_name.lower()
    alias = alias.lower()
    if game_key in aliases and alias in aliases[game_key]:
        aliases[game_key].remove(alias)
        save_aliases(aliases)
        return True
    return False

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
        logger = get_logger(__name__)
        logger.error(f"{system} is an unsupported operating system")
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

def normalize_game_name(game_name):
    """
    Normalize game name for consistent formatting and matching.
    
    :param game_name: The game name to normalize
    :return: Normalized game name
    """
    # Common transformations
    transformations = [
        lambda x: x.lower(),  # Lowercase
        lambda x: x.replace(" ", ""),  # Remove spaces
        lambda x: x.replace("2", "ii"),  # Replace numbers with roman numerals
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
    """
    Format game title for display.
    
    :param game_name: The game name to format
    :return: Formatted game title
    """
    # Convert roman numerals to numbers (case-insensitive)
    roman_to_num = {
        'ii': '2', 'iii': '3', 'iv': '4', 'v': '5',
        'vi': '6', 'vii': '7', 'viii': '8', 'ix': '9', 'x': '10'
    }
    
    # Split the title into words
    words = game_name.split()
    
    # Process each word
    for i, word in enumerate(words):
        word_lower = word.lower()
        
        # Convert roman numerals to numbers
        for roman, num in roman_to_num.items():
            if word_lower == roman:
                words[i] = num
                break
        else:  # no roman numeral found
            # Fix capitalization after apostrophes
            if "'" in word:
                parts = word.split("'")
                # Capitalize first part, keep second part's original case
                words[i] = parts[0].capitalize() + "'" + parts[1]
            else:
                words[i] = word.capitalize()
    
    return " ".join(words)

def find_closest_match(game_name):
    steam_games = game_dict.load_json_data(game_dict.STEAM_GAMES_FILE, {})
    epic_games = game_dict.load_json_data(game_dict.EPIC_GAMES_FILE, {})
    all_games = list(steam_games.keys()) + list(epic_games.keys())
    aliases = get_aliases()
    # Check for exact matches first (case-insensitive)
    for game in all_games:
        if game_name.lower() == game.lower():
            return [game]
    # Check aliases from JSON
    for game, alias_list in aliases.items():
        if game_name.lower() in [a.lower() for a in alias_list]:
            if game in all_games:
                return [game]
    # Try normalized versions
    normalized_input = normalize_game_name(game_name)
    for game in all_games:
        normalized_game = normalize_game_name(game)
        if any(n_input in n_game for n_input, n_game in zip(normalized_input, normalized_game)):
            return [game]
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
        logger = get_logger(__name__)
        logger.warning("Invalid choice. Cancelling launch.")
        return None

def find_and_confirm_game(game_name):
    """
    Find the closest matching game and confirm the choice with the user.
    
    :param game_name: The input game name
    :return: The confirmed game name or None if not found or cancelled
    """
    original_input = game_name.lower()
    matches = find_closest_match(original_input)
    logger = get_logger(__name__)
    if len(matches) == 1:
        game_name = matches[0]
        if not confirm_game_choice(game_name, original_input):
            return None
    elif len(matches) > 1:
        game_name = handle_multiple_matches(matches, original_input)
        if game_name is None:
            return None
    else:
        logger.warning(f"No matches found for '{original_input}'.")
        print_all_games()
        return None
    return game_name