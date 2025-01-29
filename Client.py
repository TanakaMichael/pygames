import time
import ctypes
from steamworks import STEAMWORKS
import json
import SteamNetworking as sn
def get_friend_lobbies() -> list[int]:
    """
    C++側の RefreshFriendLobbies() を呼んで、その結果のロビーID一覧をPythonのlistで返す
    """
    n = sn.refresh_friend_lobbies()
    result = []
    for i in range(n):
        lobby_id = sn.get_friend_lobby_id_by_index(i)
        result.append(lobby_id)
    return result

def get_friend_lobbies_richpresence() -> list[int]:
    n = sn.refresh_friend_lobbies_richpresence()
    result = []
    for i in range(n):
        lobby_id = sn.get_friend_lobby_id_by_index_richpresence(i)
        result.append(lobby_id)
    return result

def get_public_lobbies() -> list[int]:
    n = sn.refresh_public_lobbies()
    result = []
    for i in range(n):
        lobby_id = sn.get_public_lobby_id_by_index(i)
        result.append(lobby_id)
    return result

# Steam API 初期化
steamworks = STEAMWORKS()
steamworks.initialize()

if sn.initialize_steam():
    print("✅ Steam API 初期化成功")

# 自分の Steam ID を取得
client_id = sn.get_steam_id()
print(f"🎮 クライアントの Steam ID: {client_id}")

# **ロビーが存在するかチェック**
lobbies = get_friend_lobbies_richpresence()
num_lobbies = len(lobbies)
if num_lobbies > 0:
    print(f"🏠 参加可能なロビー数: {num_lobbies}")
    # lobby_id = get_lobby_by_index(0)  # 最初のロビーに参加
    lobby_id = lobbies[0] # 最初のロビーに参加
    if lobby_id != 0:
        sn.join_lobby(lobby_id)
        sn.set_lobby_rich_presence(lobby_id) # 現在参加しているlobbyの情報を通知
        print(f"✅ ロビー {lobby_id} に参加しました！")
    else:
        print("❌ 自分がオーナーのロビーがありません")
        exit()
else:
    print("❌ 参加できるロビーがありません")
    exit()

# サーバーの Steam ID を取得（ロビーのオーナー）
host_id = sn.get_lobby_owner(lobby_id)
print(f"🎮 ロビーのホスト: {host_id}")

# メッセージ送信＆受信ループ
while True:
    message = input("メッセージ: ")
    data = int(input("付属数値: "))
    if message.lower() == "exit":
        break

    # json形式で送信
    message = json.dumps({"message": message, "data": data})

    sn.send_p2p_message(host_id, message.encode())
    print(f"📨 {host_id} に送信: {message}")

    buffer = ctypes.create_string_buffer(512)
    sender_steam_id = ctypes.c_uint64()

    if sn.receive_p2p_message(buffer, 512, ctypes.byref(sender_steam_id)):
        print(f"📩 {sender_steam_id.value} から受信: ")
        data = json.loads(buffer.value.decode())  # JSON をデコード
        if data["message"] == "cmd":
            print(f"cmd数値: {data['data']}を送ってきた")

    time.sleep(0.1)
