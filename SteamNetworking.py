import ctypes
import os

# DLL をロード
dll_path = os.path.abspath("./SteamNetworkingWrapper.dll")
steam_dll = ctypes.CDLL(dll_path)

# Steam API 初期化
initialize_steam = steam_dll.InitializeSteam
initialize_steam.restype = ctypes.c_bool

# Steam ID 取得
get_steam_id = steam_dll.GetSteamID
get_steam_id.restype = ctypes.c_uint64

# メッセージ送信
send_p2p_message = steam_dll.SendP2PMessage
send_p2p_message.argtypes = [ctypes.c_uint64, ctypes.c_char_p]
send_p2p_message.restype = ctypes.c_bool

# メッセージ受信
receive_p2p_message = steam_dll.ReceiveP2PMessage
receive_p2p_message.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ctypes.c_uint64)]
receive_p2p_message.restype = ctypes.c_bool

# **ロビーの数を取得（フレンドのみ / すべて）**
get_num_lobbies = steam_dll.GetNumLobbies
get_num_lobbies.argtypes = [ctypes.c_bool]
get_num_lobbies.restype = ctypes.c_int

# **インデックスからロビー ID を取得**
get_lobby_by_index = steam_dll.GetLobbyByIndex
get_lobby_by_index.argtypes = [ctypes.c_int]
get_lobby_by_index.restype = ctypes.c_uint64

# **ロビーのオーナーを取得**
get_lobby_owner = steam_dll.GetLobbyOwner
get_lobby_owner.argtypes = [ctypes.c_uint64]
get_lobby_owner.restype = ctypes.c_uint64

# **指定オーナーのロビー ID を取得**
find_lobby_by_owner = steam_dll.FindLobbyByOwner
find_lobby_by_owner.argtypes = [ctypes.c_uint64]
find_lobby_by_owner.restype = ctypes.c_uint64

# **ロビーのメンバー数を取得**
get_num_lobby_members = steam_dll.GetNumLobbyMembers
get_num_lobby_members.argtypes = [ctypes.c_uint64]
get_num_lobby_members.restype = ctypes.c_int

# **指定インデックスのロビーメンバーの Steam ID を取得**
get_lobby_member_by_index = steam_dll.GetLobbyMemberByIndex
get_lobby_member_by_index.argtypes = [ctypes.c_uint64, ctypes.c_int]
get_lobby_member_by_index.restype = ctypes.c_uint64

# **ロビー参加を検出**
check_lobby_join = steam_dll.CheckLobbyJoin
check_lobby_join.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
check_lobby_join.restype = ctypes.c_bool

# **ロビー退室を検出**
check_lobby_leave = steam_dll.CheckLobbyLeave
check_lobby_leave.argtypes = [ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
check_lobby_leave.restype = ctypes.c_bool

# **SteamID からプレイヤー名を取得**
get_steam_name = steam_dll.GetSteamName
get_steam_name.argtypes = [ctypes.c_uint64, ctypes.c_char_p, ctypes.c_int]
get_steam_name.restype = None



# **ロビー作成**
create_lobby = steam_dll.CreateLobby
create_lobby.argtypes = [ctypes.c_int, ctypes.c_int]
create_lobby.restype = ctypes.c_uint64

# 動作確認
if initialize_steam():
    print("✅ Steam API 初期化成功")

steam_id = get_steam_id()
print(f"🎮 自分の Steam ID: {steam_id}")
