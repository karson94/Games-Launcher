# Games Launcher

A command-line tool for launching Steam and Epic Games efficiently.

## Features

- Launch Steam and Epic Games directly from the command line
- Intelligent game name matching, tolerant of typos and partial inputs
- Random roguelike launcher
- Cross-platform support (Windows, macOS, Linux)
- Smart game suggestions for misspelled names

## Prerequisites

- Python 3.6+
- Steam and/or Epic Games Launcher installed
- Games installed on your system

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Games-Launcher.git
   cd Games-Launcher
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

### Steam Setup

1. Create a `personal_config.py` file in the GamesLauncher directory:

   ```python
   STEAM_API_KEY = "your_steam_api_key_here"
   STEAM_ID = "your_steam_id_here"
   ```

   To obtain your Steam API key:
   - Visit https://steamcommunity.com/dev/apikey
   - Log in and agree to the Steam Web API Terms of Use
   - Enter a domain name (use 'localhost' for personal use)
   - Your API key will be generated

   To find your Steam ID:
   - Go to https://steamid.io/
   - Enter your Steam profile URL
   - Copy the "steamID64" value

2. Alternatively, you can edit `config.py` directly, but be cautious about sharing this file.

### Epic Games Configuration

1. Open or create `data/lists/epic_games.json` in the GamesLauncher folder and add your games:

   ```json
   {
     "game name": "epic_game_id",
     "another game": "another_epic_game_id"
   }
   ```

2. To find the Epic Games ID:
   - Open Epic Games Launcher
   - Navigate to your Library
   - Select the game
   - Click the three dots (...) and choose "Manage"
   - Select "Create Desktop Shortcut"
   - Right-click the new shortcut and select "Properties"
   - In the "Target" field, locate the ID in the URL:
     ```
     com.epicgames.launcher://apps/[epic_game_id]?action=launch&silent=true
     ```

   Example:
   ```json
   {
     "Slime Rancher": "corydalis%3A1e38b618d106430db94b474abbfecc16%3ACorydalis"
   }
   ```

### Steam Games Configuration

1. To find a Steam App ID:
   - Go to the game's Steam store page
   - The App ID is the number after `/app/` in the URL
   - Example: For "Slay the Spire", the URL is `https://store.steampowered.com/app/646570/Slay_the_Spire/`, so the App ID is `646570`

2. Open `data/lists/steam_roguelikes.json` or `data/lists/steam_games.json` in the GamesLauncher folder and add games:
   ```json
   {
     "game name": "steam_app_id",
     "another game": "another_steam_app_id"
   }
   ```

   Example:
   ```json
   {
     "slay the spire": "646570",
     "hades": "1145360"
   }
   ```

### Launch Options Configuration

1. Open `data/launch_options.json` in the GamesLauncher folder to add special launch options for games:

   ```json
   {
     "game name": "launch options",
     "another game": "other launch options",
     "special game": {
       "alternate_app_id": "alternate_steam_app_id",
       "name": "Alternate Game Name"
     }
   }
   ```

   Example:
   ```json
   {
     "playerunknown's battlegrounds": "-KoreanRating",
     "pubg": "-KoreanRating",
     "slay the spire": {
       "alternate_app_id": "1605060",
       "name": "Mod the Spire"
     }
   }
   ```

   These launch options will be applied when starting the game through the launcher. For special cases like "Slay the Spire", an alternate Steam app ID can be specified to launch a different executable (e.g., "Mod the Spire").

## Usage

### Command Line

Run the script with a game name as an argument:
```
python game_launcher.py "Slay The Spire"
```

### PowerShell Integration (Recommended for Windows users)

1. Open your PowerShell profile:
   ```powershell
   notepad $PROFILE
   ```

2. Add this function:
   ```powershell
   function game {
       param($gameName)
       python C:\path\to\Games-Launcher\game_launcher.py $gameName
   }
   ```

3. Replace `C:\path\to\Games-Launcher` with the actual path to the script.

4. Save and restart PowerShell.

Now you can launch games with:
```
game Slay The Spire
```

### Key Features

The launcher offers flexible input handling:

- Partial names are accepted: `game slay` launches "Slay the Spire"
- Typo-tolerant: `game hads` correctly identifies "Hades"
- Recognizes common acronyms: `game gtav` for "Grand Theft Auto V"
- Case-insensitive: `game GRAND THEFT AUTO V` works as expected
- Handles multi-word titles without quotes: `game slay the spire`

Additional feature: Use `game random` to launch a random roguelike.

Note: The launcher will always confirm before launching if there's any ambiguity.

## Troubleshooting

If you encounter issues:
- Verify that Steam and Epic Games Launcher are properly installed
- Ensure game paths in `game_launcher.py` match your installation directories
- For Epic Games, confirm that game names in `data/lists/epic_games.json` are accurate

## Contributing

Contributions are welcome. Please submit a pull request with your proposed changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

