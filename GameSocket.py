import asyncio
import websockets
from websockets.asyncio.server import serve
from datetime import datetime
import json


# 保存所有已連線的用戶
connected_users = {}    #用socket編號當作索引key
permission_queue = []  # 用於管理權限轉移


async def chat_handler(websocket):
    global permission_queue

    # 接收用戶名稱
    username = await websocket.recv()   #等待前端輸入名稱
    connected_users[websocket] = username

    # 廣播新用戶加入的消息
    join_message = f"{username} has joined the chat!"
    await broadcast(format_message("Server", join_message))

    board_data = {"Board": [[0 for _ in range(10)] for _ in range(10)]}

    # 若加入的用戶少於兩人，則將其加入權限轉移隊列
    if websocket not in permission_queue and len(permission_queue) < 2:
        permission_queue.append(websocket)
        if len(permission_queue) == 1:
            # 第一位用戶自動獲得初始權限
            await websocket.send(json.dumps({"action": "allow"}))

    if len(permission_queue) >= 2:
        await permission_queue[0].send(json.dumps({"color": -1})) #第一位進入執黑
        await permission_queue[1].send(json.dumps({"color": 1}))  #第二位進入執白


    try:
        while True:
            message = await websocket.recv()
            #前端回傳game_board: {"board": [[]]} or winner: {"Winner": (-1 or 1)}

            if websocket in permission_queue and websocket == permission_queue[0]:
                # 用戶擁有權限，可以傳送座標
                try:
                    data = json.loads(message)
                    
                    if "Winner" in data:    
                        await broadcast(json.dumps(data))
                        continue
                    
                    if "board" in data: #回傳資料為board
                        board_data = {
                            "Board": data["board"]  # 使用鍵名 Board 傳遞棋盤
                        }
                        
                        print("="*19)
                        for row in data["board"]:
                            print(" ".join(map(str, row)))
                        print("="*19)
                        
                        
                        await broadcast(json.dumps(board_data))  # 將資料轉為 JSON 字串
                        # 權限轉移邏輯
                        permission_queue.append(permission_queue.pop(0))                    
                        await permission_queue[0].send(json.dumps({"action": "allow"}))
                        continue
                    
                except json.JSONDecodeError:
                    pass  # 若訊息不是 JSON 格式，繼續處理為普通訊息

            elif websocket not in permission_queue or websocket != permission_queue[0]:
                # 非權限用戶試圖傳送座標
                try:
                    data = json.loads(message)
                    if "x" in data and "y" in data:
                        # 回傳提示，表示無法傳送座標
                        await websocket.send(
                            format_message("Server", "You do not have permission to send coordinates.")
                        )
                        continue
                except json.JSONDecodeError:
                    pass

            # 處理普通訊息
            broadcast_message = format_message(username, message)
            await broadcast(broadcast_message)

    except websockets.ConnectionClosed:
        pass
    finally:
        # 當用戶斷線時移除並廣播消息
        del connected_users[websocket]
        if websocket in permission_queue:
            permission_queue.remove(websocket)

            # 若權限持有者斷線，將權限移交給下一位
            if permission_queue:
                await permission_queue[0].send(json.dumps({"action": "allow"}))

        leave_message = f"{username} has left the chat."
        await broadcast(format_message("Server", leave_message))


async def broadcast(message):
    # 廣播訊息給所有已連線的用戶
    
    for websocket in connected_users:
        await websocket.send(message)


def format_message(sender, message):
    # 格式化訊息，加入時間戳和發送者名稱
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"[{timestamp}] {sender}: {message}"


async def main():
    print("WebSocket 伺服器啟動，等待用戶端連線...")
    async with serve(chat_handler, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())