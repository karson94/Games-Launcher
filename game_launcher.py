import sys
import random
import os
import platform
import subprocess
from difflib import get_close_matches
import requests
import json
import game_dict
from config import STEAM_API_KEY, STEAM_ID

# Get the appropriate system command based on the operating system
def get_system_command():
    system = platform.system()
    if system == "Windows":
        return "start"
    elif system == "Darwin":  # macOS
        return "open"
    elif system == "Linux":
        return "xdg-open"
    else:
        print(f"{system} is an unsupported operating system")
        return None

# Launch a Steam game using the appropriate system command
def launch_steam_game(app_id):
    command = get_system_command()
    if command:
        steam_url = f'steam://rungameid/{app_id}'
        if command == "start":
            subprocess.run([command, "", steam_url], shell=True)
        else:
            subprocess.run([command, steam_url])

# Launch an Epic game using the appropriate system command
def launch_epic_game(app_name):
    command = get_system_command()
    if command:
        epic_url = f"com.epicgames.launcher://apps/{app_name}?action=launch&silent=true"
        if command == "start":
            subprocess.run([command, "", epic_url], shell=True)
        else:
            subprocess.run([command, epic_url])
    else:
        print("Epic Games Launcher is not supported on this system")

# Print all available games
def print_all_games():
    print("Available games:")
    for game in sorted(STEAM_GAME_DICT.keys()):
        print(f"- {game}")

# Find the closest matching game name from the available games
def find_closest_match(game_name):
    all_games = list(STEAM_GAME_DICT.keys()) + list(EPIC_GAME_DICT.keys())
    
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
    if game_name in STEAM_GAME_DICT:
        app_id = STEAM_GAME_DICT[game_name]
        print(f"Launching {game_name.title()} from Steam...")
        launch_steam_game(app_id)
    elif game_name in EPIC_GAME_DICT:
        app_id = EPIC_GAME_DICT[game_name]
        print(f"Launching {game_name.title()} from Epic Games...")
        launch_epic_game(app_id)
    else:
        app_id = fetch_steam_game(game_name)
        if app_id:
            STEAM_GAME_DICT[game_name] = app_id
            save_json_data(STEAM_GAMES_FILE, STEAM_GAME_DICT)
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
    roguelike = random.choice(list(STEAM_ROUGLIKES.keys()))
    print(f"Launching random roguelike: {roguelike.title()}")
    launch_game(roguelike)

# File paths for JSON data
STEAM_GAMES_FILE = 'steam_games.json'
EPIC_GAMES_FILE = 'epic_games.json'
STEAM_ROGUELIKES_FILE = 'steam_roguelikes.json'

# Add this check:
if not STEAM_API_KEY or not STEAM_ID:
    print("Error: STEAM_API_KEY or STEAM_ID not set. Please set them in config.py or personal_config.py")
    sys.exit(1)

# Load game dictionaries
STEAM_GAME_DICT, EPIC_GAME_DICT, STEAM_ROGUELIKES = game_dict.update_game_lists(STEAM_API_KEY, STEAM_ID)

# Save updated game dictionaries
game_dict.save_json_data(STEAM_GAMES_FILE, STEAM_GAME_DICT)
game_dict.save_json_data(EPIC_GAMES_FILE, EPIC_GAME_DICT)
game_dict.save_json_data(STEAM_ROGUELIKES_FILE, STEAM_ROGUELIKES)

# Main execution block
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python game_launcher.py <game_name>")
        sys.exit(1)

    game_name = " ".join(sys.argv[1:])  # Join all arguments as the game name
    launch_game(game_name)