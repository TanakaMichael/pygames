import math
import uuid
import base64
import json
import SteamNetworking as sn

# 送受信時のバッファサイズ（既存のコードで使っているサイズに合わせる）
FRAGMENT_BUFFER_SIZE = 2048

def send_large_message(target_id, data, buffer_size=FRAGMENT_BUFFER_SIZE):
    """
    大きな JSON データを断片化して送信する。
    """
    # JSON化してバイト列に変換
    message_bytes = json.dumps(data).encode('utf-8')
    # ヘッダー情報分の余裕を header_size 分確保（必要に応じて調整）
    header_size = 200  
    max_payload = buffer_size - header_size
    total_fragments = math.ceil(len(message_bytes) / max_payload)
    # 各メッセージに一意なIDを付与
    message_id = str(uuid.uuid4())
    
    for fragment_index in range(total_fragments):
        start = fragment_index * max_payload
        end = start + max_payload
        fragment_bytes = message_bytes[start:end]
        
        # バイナリデータを JSON で送信できるよう base64 エンコード
        encoded_fragment = base64.b64encode(fragment_bytes).decode('utf-8')
        
        fragment_message = {
            "type": "fragment",
            "message_id": message_id,
            "total_fragments": total_fragments,
            "fragment_index": fragment_index,
            "data": encoded_fragment
        }
        # ここで各断片を送信
        sn.send_p2p_message(target_id, json.dumps(fragment_message).encode('utf-8'))

# 受信側で断片を一時保存するためのグローバル辞書
received_fragments = {}

def handle_incoming_fragment(fragment):
    """
    受信した断片を受け取り、全断片がそろったら連結して元のメッセージを再構築する。
    """
    message_id = fragment["message_id"]
    total_fragments = fragment["total_fragments"]
    fragment_index = fragment["fragment_index"]
    encoded_data = fragment["data"]
    
    # base64デコードで元のバイト列に戻す
    fragment_data = base64.b64decode(encoded_data)
    
    if message_id not in received_fragments:
        received_fragments[message_id] = {}
    received_fragments[message_id][fragment_index] = fragment_data
    
    print(f"🔗 断片 {fragment_index+1}/{total_fragments} を受信 (メッセージID: {message_id})")
    
    # 全断片がそろったかチェック
    if len(received_fragments[message_id]) == total_fragments:
        # 断片番号順に並べて連結
        all_fragments = [received_fragments[message_id][i] for i in range(total_fragments)]
        complete_bytes = b''.join(all_fragments)
        # 保存していた断片情報を削除
        del received_fragments[message_id]
        try:
            complete_message = json.loads(complete_bytes.decode('utf-8'))
            return complete_message
        except json.JSONDecodeError:
            print("❌ 再構築したメッセージの JSON 解析に失敗")
            return None
    else:
        # まだ全断片がそろっていない場合は None を返す
        return None
