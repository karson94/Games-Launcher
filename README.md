# Games Launcher

A sophisticated command-line tool for launching Steam and Epic Games efficiently across multiple platforms.

## Features

- Launch Steam and Epic Games directly from the command line
- Intelligent game name matching, tolerant of typos and partial inputs
- Special handling for Mod the Spire integration with Slay the Spire
- Random roguelike game launcher
- Cross-platform support (Windows, macOS, Linux)
- List games from Steam or Epic libraries

## Prerequisites

- Python 3.6+
- Steam and/or Epic Games Launcher installed
- Java Runtime Environment (JRE) for Mod the Spire functionality

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/[yourusername]/Games-Launcher.git
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

   To obtain your Steam API key and ID, visit:
   - API Key: https://steamcommunity.com/dev/apikey
   - Steam ID: https://steamid.io/

2. The launcher will automatically fetch your Steam games using the Steam API.

### Epic Games Setup

1. Open or create `data/lists/epic_games.json` and add your games:

   ```json
   {
     "Game Name": "epic_game_id"
   }
   ```

2. To find the Epic Games ID:
   - Open Epic Games Launcher
   - Navigate to your Library
   - Right-click on the game you want to add
   - Select "Create Desktop Shortcut"
   - Right-click the new shortcut and select "Properties"
   - In the "Target" field, locate the ID in the URL:
     ```
     com.epicgames.launcher://apps/[epic_game_id]?action=launch&silent=true
     ```
   - Copy the `[epic_game_id]` part and use it in your `epic_games.json` file

   Example:
   ```json
   {
     "slime rancher": "corydalis%3A1e38b618d106430db94b474abbfecc16%3ACorydalis"
   }
   ```

### Launch Options

1. Edit `data/launch_options.json` to add special launch options for games:

   ```json
   {
     "playerunknown's battlegrounds": "-KoreanRating"
   }
   ```

## Usage

### Command Line

The basic syntax for using the launcher is:

```
python launcher.py <command> [arguments]
```

Available commands:

1. Launch a game:
   ```
   python launcher.py <game_name>
   ```
   Example: `python launcher.py "Slay the Spire"`

2. Launch a random roguelike:
   ```
   python launcher.py random
   ```

3. List games:
   ```
   python launcher.py list <steam|epic|all>
   ```
   Example: `python launcher.py list steam`

### PowerShell Integration (Windows)

Add this function to your PowerShell profile:

```powershell
function game {
    $pythonScript = "C:\path\to\Games-Launcher\launcher.py"
    if ($args.Count -gt 0) {
        python $pythonScript $args
    } else {
        Write-Host "Usage: game <game_name>"
        Write-Host "       game random"
        Write-Host "       game list <steam|epic|all>"
    }
}
```

Then use:

```
game Slay The Spire
game random
game list all
```

## Key Features

- Partial names: `game slay` launches "Slay the Spire"
- Typo-tolerant: `game hads` identifies "Hades"
- Common acronyms: `game gtav` for "Grand Theft Auto V"
- Case-insensitive: `game GRAND THEFT AUTO V` works
- Multi-word titles: `game slay the spire` (no quotes needed)
- Mod the Spire: Automatically launches with mods if available
- Random roguelike: `game random`
- List games: `game list steam`, `game list epic`, or `game list all`

Note: The launcher confirms before launching if there's any ambiguity.

## Troubleshooting

- Verify Steam and Epic Games Launcher installations
- Check Java installation for Mod the Spire functionality
- Ensure game paths in configuration files are correct
- If a game doesn't launch, check the corresponding JSON file to ensure the game ID is correct

## Contributing

Contributions are welcome. Please submit a pull request with your proposed changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

