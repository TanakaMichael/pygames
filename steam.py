import os
os.add_dll_directory(os.getcwd())

from steamworks import STEAMWORKS
from steamworks.exceptions import SteamNotRunningException
steamworks = STEAMWORKS()
try:
    steamworks.initialize() # 何かしらのエラーが発生した場合は終了
except OSError:
    exit()
except SteamNotRunningException:
    exit()
