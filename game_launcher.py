import sys
import random
import os
import platform
import subprocess
from game_dict import STEAM_GAME_DICT, STEAM_ROUGLIKES, EPIC_GAME_DICT
from difflib import get_close_matches

def find_closest_match(game_name):
    all_games = list(STEAM_GAME_DICT.keys()) + list(EPIC_GAME_DICT.keys())
    return get_close_matches(game_name.lower(), all_games, n=2, cutoff=0.65)

def print_all_games():
    print("Available games:")
    for game in sorted(STEAM_GAME_DICT.keys()):
        print(f"- {game}")

def launch_random_roguelike():
    roguelike = random.choice(list(STEAM_ROUGLIKES.keys()))
    print(f"Launching random roguelike: {roguelike.title()}")
    launch_game(roguelike)

def launch_game(game_name):
    game_name = game_name.lower()
    if game_name == "roguelikes":
        launch_random_roguelike()
    elif game_name in STEAM_GAME_DICT:
        app_id = STEAM_GAME_DICT[game_name]
        print(f"Launching {game_name.title()} from Steam...")
        launch_steam_game(app_id)
    elif game_name in EPIC_GAME_DICT:
        app_id = EPIC_GAME_DICT[game_name]
        print(f"Launching {game_name.title()} from Epic Games...")
        launch_epic_game(app_id)
    else:
        closest_match = find_closest_match(game_name)
        if closest_match:
            print(f"Game '{game_name}' not found. Did you mean '{closest_match[0]}'?")
            user_input = input("Press Enter to launch this game, or type 'n' to cancel: ").lower()
            if user_input.lower()!= 'n':
                launch_game(closest_match[0])
        else:
            print(f"Game '{game_name}' not found in the list of known games.")
            print_all_games()

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

def launch_steam_game(app_id):
    command = get_system_command()
    if command:
        steam_url = f'steam://rungameid/{app_id}'
        if command == "start":
            subprocess.run([command, "", steam_url], shell=True)
        else:
            subprocess.run([command, steam_url])

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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python game_launcher.py <game_name>")
        sys.exit(1)

    game_name = " ".join(sys.argv[1:]).lower()  # Join all arguments as the game name and convert to lowercase
    launch_game(game_name)