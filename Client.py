import time
import ctypes
from steamworks import STEAMWORKS
import json
from SteamNetworking import initialize_steam, get_steam_id, send_p2p_message, receive_p2p_message, get_num_lobbies, get_lobby_by_index, get_lobby_owner, find_lobby_by_owner

# Steam API 初期化
steamworks = STEAMWORKS()
steamworks.initialize()

if initialize_steam():
    print("✅ Steam API 初期化成功")

# 自分の Steam ID を取得
client_id = get_steam_id()
print(f"🎮 クライアントの Steam ID: {client_id}")

# **ロビーが存在するかチェック**
num_lobbies = get_num_lobbies(False)
if num_lobbies > 0:
    print(f"🏠 参加可能なロビー数: {num_lobbies}")
    # lobby_id = get_lobby_by_index(0)  # 最初のロビーに参加
    lobby_id = find_lobby_by_owner(client_id) # 自分がオーナーのロビーに参加
    if lobby_id != 0:
        print(f"✅ 自分がオーナーのロビー {lobby_id} を発見！")
        steamworks.Matchmaking.JoinLobby(lobby_id)
        print(f"✅ ロビー {lobby_id} に参加しました！")
    else:
        print("❌ 自分がオーナーのロビーがありません")
else:
    print("❌ 参加できるロビーがありません")
    exit()

# サーバーの Steam ID を取得（ロビーのオーナー）
host_id = get_lobby_owner(lobby_id)
print(f"🎮 ロビーのホスト: {host_id}")

# メッセージ送信＆受信ループ
while True:
    message = input("メッセージ: ")
    data = int(input("付属数値: "))
    if message.lower() == "exit":
        break

    # json形式で送信
    message = json.dumps({"message": message, "data": data})

    send_p2p_message(host_id, message.encode())
    print(f"📨 {host_id} に送信: {message}")

    buffer = ctypes.create_string_buffer(512)
    sender_steam_id = ctypes.c_uint64()

    if receive_p2p_message(buffer, 512, ctypes.byref(sender_steam_id)):
        print(f"📩 {sender_steam_id.value} から受信: ")
        data = json.loads(buffer.value.decode())  # JSON をデコード
        if data["message"] == "cmd":
            print(f"cmd数値: {data['data']}を送ってきた")

    time.sleep(0.1)
