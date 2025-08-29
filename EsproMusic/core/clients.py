# EsproMusic/core/clients.py

from EsproMusic.core.bot import Loy
from EsproMusic.core.userbot import Userbot
from EsproMusic.core.dir import dirr
from EsproMusic.core.git import git
import EsproMusic.platforms import platforms

# Run setup
dirr()
git()

# Clients
app = Loy()
userbot = Userbot()

# APIs
Apple = platforms.AppleAPI()
Carbon = platforms.CarbonAPI()
SoundCloud = platforms.SoundAPI()
Spotify = platforms.SpotifyAPI()
Resso = platforms.RessoAPI()
Telegram = platforms.TeleAPI()
YouTube = platforms.YouTubeAPI()