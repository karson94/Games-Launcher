from game_dict import fetch_steam_games
from config import STEAM_API_KEY, STEAM_ID

games = fetch_steam_games(STEAM_API_KEY, STEAM_ID)
print(f"Fetched {len(games)} games.")
print(games) 