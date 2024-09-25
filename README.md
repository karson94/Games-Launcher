# Games Launcher

A simple command-line tool to launch your favorite games from Steam and Epic Games Store.

## Features

- Launch Steam and Epic Games directly from the command line
- Fuzzy matching for game names
- Random roguelike launcher
- Cross-platform support (Windows, macOS, Linux)

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

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Open `game_dict.py` and add your games to the appropriate dictionaries:

   - For Steam games:
     ```python
     STEAM_GAME_DICT = {
         "game nickname": "steam_app_id",
         # Add more games...
     }
     ```

   - For Epic Games:
     ```python
     EPIC_GAME_DICT = {
         "game nickname": "EpicInternalName",
         # Add more games...
     }
     ```

2. (Optional) Add roguelike games to the `STEAM_ROUGLIKES` dictionary in `game_dict.py`.

## Usage

### Command Line

Run the script with a game name as an argument:
```
python game_launcher.py "game name"
```

### PowerShell Integration

To use the game launcher directly from PowerShell:

1. Open your PowerShell profile:
   ```powershell
   notepad $PROFILE
   ```

2. Add the following function to the file:
   ```powershell
   function game {
       param($gameName)
       python C:\path\to\Games-Launcher\game_launcher.py $gameName
   }
   ```

3. Replace `C:\path\to\Games-Launcher` with the actual path to the script on your system.

4. Save the file and restart PowerShell.

Now you can launch games by typing:
```
game "game name"
```

## Troubleshooting

- Ensure Steam and Epic Games Launcher are installed and properly configured.
- Check that the game paths in `game_launcher.py` match your system's installation paths.
- For Epic Games, verify that the internal game names in `EPIC_GAME_DICT` are correct.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

