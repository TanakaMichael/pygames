import os
os.add_dll_directory(os.getcwd())

from steamworks import STEAMWORKS
from steamworks.exceptions import SteamNotRunningException
steamworks = STEAMWORKS()
try:
    steamworks.initialize()
except OSError:
    exit()
except SteamNotRunningException:
    exit()
