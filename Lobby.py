import time
import ctypes
from steamworks import STEAMWORKS
from SteamNetworking import get_lobby_member_by_index, get_num_lobby_members

# Steamworks API の初期化
steamworks = STEAMWORKS()
steamworks.initialize()

# SteamNetworking DLL のロード
from SteamNetworking import initialize_steam, get_steam_id, send_p2p_message, receive_p2p_message, create_lobby, check_lobby_join, get_steam_name, check_lobby_leave

if initialize_steam():
    print("✅ Steam API 初期化成功")

# 自分の Steam ID を取得
server_id = get_steam_id()
print(f"🎮 サーバーの Steam ID: {server_id}")

# **ロビーを作成**
LOBBY_TYPE = 1  # 1 = フレンドのみ, 2 = 公開, 3 = 非公開
MAX_PLAYERS = 4
lobby_id = create_lobby(LOBBY_TYPE, MAX_PLAYERS)

if lobby_id == 0:
    print("❌ ロビーの作成に失敗しました")
    exit()

print(f"🏠 ロビーを作成しました！ ロビー ID: {lobby_id}")

# クライアントリストを取得
def get_clients():
    return [
        get_lobby_member_by_index(lobby_id, i)
        for i in range(get_num_lobby_members(lobby_id))
    ]

# メッセージ受信ループ
while True:
    buffer = ctypes.create_string_buffer(512)
    sender_steam_id = ctypes.c_uint64()

    # メッセージ受信
    if receive_p2p_message(buffer, 512, ctypes.byref(sender_steam_id)):
        message = buffer.value.decode()
        print(f"📩 {sender_steam_id.value} から受信: {message}")

        # クライアント全員にメッセージをブロードキャスト
        for player_id in get_clients():
            if player_id and player_id != server_id:
                send_p2p_message(player_id, message.encode())
    joined_steam_id = ctypes.c_uint64()
    joined_lobby_id = ctypes.c_uint64()

    # **ロビー参加チェック**
    if check_lobby_join(ctypes.byref(joined_steam_id), ctypes.byref(joined_lobby_id)):
        name_buffer = ctypes.create_string_buffer(128)
        get_steam_name(joined_steam_id.value, name_buffer, 128)
        print(f"🎉 {name_buffer.value.decode()} がロビー {joined_lobby_id.value} に参加しました！")

    # **ロビー退室チェック**
    left_steam_id = ctypes.c_uint64()
    left_lobby_id = ctypes.c_uint64()

    if check_lobby_leave(ctypes.byref(left_steam_id), ctypes.byref(left_lobby_id)):
        name_buffer = ctypes.create_string_buffer(128)
        get_steam_name(left_steam_id.value, name_buffer, 128)
        print(f"🚪 {name_buffer.value.decode()} がロビー {left_lobby_id.value} から退出しました！")

    time.sleep(0.05)
