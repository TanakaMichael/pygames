import time
import ctypes
import json
from steamworks import STEAMWORKS
import SteamNetworking as sn

# Steam API 初期化
steamworks = STEAMWORKS()
steamworks.initialize()

if sn.initialize_steam():
    print("✅ Steam API 初期化成功")

# 自分の Steam ID を取得
server_id = sn.get_steam_id()
print(f"🎮 サーバーの Steam ID: {server_id}")

# **ロビーを作成**
LOBBY_TYPE = 1  # 1 = フレンドのみ, 2 = 公開, 3 = 非公開
MAX_PLAYERS = 4
lobby_id = sn.create_lobby(LOBBY_TYPE, MAX_PLAYERS)
sn.set_lobby_rich_presence(lobby_id)  # ロビー情報を通知
if lobby_id == 0:
    print("❌ ロビーの作成に失敗しました")
    exit()

print(f"🏠 ロビーを作成しました！ ロビー ID: {lobby_id}")

# クライアントリストを取得
def get_clients():
    return [
        sn.get_lobby_member_by_index(lobby_id, i)
        for i in range(sn.get_num_lobby_members(lobby_id))
    ]

# PING の送信ループ
def send_ping():
    while True:
        for player_id in get_clients():
            if player_id and player_id != server_id:
                ping_message = json.dumps({"message": "PING"})
                sn.send_p2p_message(player_id, ping_message.encode())

        time.sleep(1)  # **2秒ごとに PING を送信**
# **P2P セッションを確立**
def accept_p2p_sessions():
    while True:
        for player_id in get_clients():
            if player_id and player_id != server_id:
                sn.accept_p2p_session(player_id)
        time.sleep(0.1)

import threading
session_thread = threading.Thread(target=accept_p2p_sessions, daemon=True)
session_thread.start()

# **PING 送信を並列実行**
ping_thread = threading.Thread(target=send_ping, daemon=True)
ping_thread.start()

# メッセージ受信ループ
while True:
    buffer = ctypes.create_string_buffer(512)
    sender_steam_id = ctypes.c_uint64()

    # メッセージ受信
    if sn.receive_p2p_message(buffer, 512, ctypes.byref(sender_steam_id)):
        data = json.loads(buffer.value.decode())

        # **PING は無視**
        if data["message"] == "PING":
            continue

        print(f"📩 {sender_steam_id.value} から受信: {data}")

        # クライアント全員にメッセージをブロードキャスト
        for player_id in get_clients():
            if player_id and player_id != server_id:
                sn.send_p2p_message(player_id, json.dumps(data).encode())

    joined_steam_id = ctypes.c_uint64()
    joined_lobby_id = ctypes.c_uint64()

    # **ロビー参加チェック**
    if sn.check_lobby_join(ctypes.byref(joined_steam_id), ctypes.byref(joined_lobby_id)):
        name_buffer = ctypes.create_string_buffer(128)
        sn.get_steam_name(joined_steam_id.value, name_buffer, 128)
        print(f"🎉 {name_buffer.value.decode()} がロビー {joined_lobby_id.value} に参加しました！")

    # **ロビー退室チェック**
    left_steam_id = ctypes.c_uint64()
    left_lobby_id = ctypes.c_uint64()

    if sn.check_lobby_leave(ctypes.byref(left_steam_id), ctypes.byref(left_lobby_id)):
        name_buffer = ctypes.create_string_buffer(128)
        sn.get_steam_name(left_steam_id.value, name_buffer, 128)
        print(f"🚪 {name_buffer.value.decode()} がロビー {left_lobby_id.value} から退出しました！")

    time.sleep(0.05)
