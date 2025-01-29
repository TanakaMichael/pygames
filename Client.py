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
client_id = sn.get_steam_id()
print(f"🎮 クライアントの Steam ID: {client_id}")

# **ロビーが存在するかチェック**
lobbies = sn.get_friend_lobbies_richpresence()
if len(lobbies) > 0:
    lobby_id = lobbies[0]
    sn.join_lobby(lobby_id)
    sn.set_lobby_rich_presence(lobby_id)  # ロビー情報を通知
    print(f"✅ ロビー {lobby_id} に参加しました！")
else:
    print("❌ 参加できるロビーがありません")
    exit()

# サーバーの Steam ID を取得（ロビーのオーナー）
host_id = sn.get_lobby_owner(lobby_id)
print(f"🎮 ロビーのホスト: {host_id}")

# **PING の監視**
last_ping_time = time.time()

# メッセージ送信＆受信ループ
while True:
    message = input("メッセージ: ")
    data = int(input("付属数値: "))

    if message.lower() == "exit":
        break
    # **最初に数回 PING を送信し、接続を安定させる**
    for _ in range(3):
        json_message = json.dumps({"message": "PING"})
        sn.send_p2p_message(host_id, json_message.encode())
        time.sleep(0.1)
    # JSON 形式で送信
    json_message = json.dumps({"message": message, "data": data})
    sn.send_p2p_message(host_id, json_message.encode())
    print(f"📨 {host_id} に送信: {json_message}")

    # 受信ループ
    buffer = ctypes.create_string_buffer(512)
    sender_steam_id = ctypes.c_uint64()

    while sn.receive_p2p_message(buffer, 512, ctypes.byref(sender_steam_id)):
        data = json.loads(buffer.value.decode())

        # **PING の処理**
        if data["message"] == "PING":
            last_ping_time = time.time()  # **最後の PING を受け取った時間を更新**
            continue

        print(f"📩 {sender_steam_id.value} から受信: {data}")

    # **一定時間 PING を受け取らなかったら切断と判定**
    if time.time() - last_ping_time > 5:  # **5秒以上 PING がない**
        print("❌ サーバーが落ちました！")
        break

    time.sleep(0.1)
