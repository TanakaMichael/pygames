import ctypes
import os
try:
    # DLL をロード
    dll_path = os.path.abspath("./SteamNetworkingWrapper.dll")
    steam_dll = ctypes.CDLL(dll_path)
    # SteamCallbacks を実行
    run_steam_callbacks = steam_dll.RunSteamCallbacks
    run_steam_callbacks.restype = None
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

    # (1) フレンドロビーの検索
    refresh_friend_lobbies = steam_dll.RefreshFriendLobbies
    refresh_friend_lobbies.restype = ctypes.c_int  # 戻り値はロビー数

    # (2) フレンドロビーID取得
    get_friend_lobby_id_by_index = steam_dll.GetFriendLobbyIDByIndex
    get_friend_lobby_id_by_index.argtypes = [ctypes.c_int]
    get_friend_lobby_id_by_index.restype = ctypes.c_uint64

    # (3) パブリックロビーの検索
    refresh_public_lobbies = steam_dll.RefreshPublicLobbies
    refresh_public_lobbies.restype = ctypes.c_int

    # (4) パブリックロビーID取得
    get_public_lobby_id_by_index = steam_dll.GetPublicLobbyIDByIndex
    get_public_lobby_id_by_index.argtypes = [ctypes.c_int]
    get_public_lobby_id_by_index.restype = ctypes.c_uint64


    # **ロビー作成**
    create_lobby = steam_dll.CreateLobby
    create_lobby.argtypes = [ctypes.c_int, ctypes.c_int]
    create_lobby.restype = ctypes.c_uint64


    # (A) JoinLobby
    join_lobby = steam_dll.JoinLobby
    join_lobby.argtypes = [ctypes.c_uint64]
    join_lobby.restype = ctypes.c_bool

    # (B) SetLobbyRichPresence
    set_lobby_rich_presence = steam_dll.SetLobbyRichPresence
    set_lobby_rich_presence.argtypes = [ctypes.c_uint64]
    set_lobby_rich_presence.restype = None

    # (C) ClearRichPresence
    clear_rich_presence = steam_dll.ClearRichPresence
    clear_rich_presence.restype = None

    # (D) GetFriendLobbyRichPresence
    get_friend_lobby_rich_presence = steam_dll.GetFriendLobbyRichPresence
    get_friend_lobby_rich_presence.argtypes = [ctypes.c_uint64]
    get_friend_lobby_rich_presence.restype = ctypes.c_uint64

    # (E) RefreshFriendLobbiesRichPresence
    refresh_friend_lobbies_richpresence = steam_dll.RefreshFriendLobbiesRichPresence
    refresh_friend_lobbies_richpresence.restype = ctypes.c_int

    # (F) GetFriendLobbyIDByIndex_RichPresence
    get_friend_lobby_id_by_index_richpresence = steam_dll.GetFriendLobbyIDByIndex_RichPresence
    get_friend_lobby_id_by_index_richpresence.argtypes = [ctypes.c_int]
    get_friend_lobby_id_by_index_richpresence.restype = ctypes.c_uint64

    accept_p2p_session = steam_dll.AcceptP2PSession
    accept_p2p_session.argtypes = [ctypes.c_uint64]
    accept_p2p_session.restype = ctypes.c_bool

    # --- サーバーシャットダウン ---
    shutdown_server = steam_dll.ShutdownServer
    shutdown_server.restype = None

    # --- コールバックスレッド停止 ---
    stop_callbacks_thread = steam_dll.StopCallbacksThread
    stop_callbacks_thread.restype = None

    # --- ロビーから退室 ---
    leave_lobby = steam_dll.LeaveLobby
    leave_lobby.argtypes = [ctypes.c_uint64]
    leave_lobby.restype = None
except ImportError:
    print("❌ SteamNetworkingWrapper.dll が見つかりません")
    exit()
except OSError:
    print("�� SteamNetworkingWrapper.dll の読み込みに失敗しました")
    exit()
except Exception as e:
    print(e)
    exit()
# 動作確認
if initialize_steam():
    print("✅ Steam API 初期化成功")

steam_id = get_steam_id()
print(f"🎮 自分の Steam ID: {steam_id}")

def get_friend_lobbies() -> list[int]:
    """
    C++側の RefreshFriendLobbies() を呼んで、その結果のロビーID一覧をPythonのlistで返す
    """
    n = refresh_friend_lobbies()
    result = []
    for i in range(n):
        lobby_id = get_friend_lobby_id_by_index(i)
        result.append(lobby_id)
    return result

def get_friend_lobbies_richpresence() -> list[int]:
    n = refresh_friend_lobbies_richpresence()
    result = []
    for i in range(n):
        lobby_id = get_friend_lobby_id_by_index_richpresence(i)
        result.append(lobby_id)
    return result

def get_public_lobbies() -> list[int]:
    n = refresh_public_lobbies()
    result = []
    for i in range(n):
        lobby_id = get_public_lobby_id_by_index(i)
        result.append(lobby_id)
    return result