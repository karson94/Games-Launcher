# Default values (for public use)
STEAM_API_KEY = ""
STEAM_ID = ""

# Try to import personal config, which overrides the above if it exists
try:
    from personal_config import STEAM_API_KEY, STEAM_ID
except ImportError:
    pass