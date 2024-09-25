import sys
import random
import os
from game_dict import STEAM_GAME_DICT, STEAM_ROUGLIKES
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
        print(f"Launching {game_name}...")
        os.system(f'start steam://rungameid/{app_id}')
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python game_launcher.py <game_name>")
        sys.exit(1)

    game_name = " ".join(sys.argv[1:])  # Join all arguments as the game name
    launch_game(game_name)