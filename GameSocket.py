import asyncio
import websockets
from websockets.asyncio.server import serve
from datetime import datetime
import json, os
from Gomoku import Gomoku_game

# 保存所有已連線的用戶
connected_users = {}    #用socket編號當作索引key
permission_queue = []  # 用於管理權限轉移

game = Gomoku_game(15)
game_status = 2 # 遊戲正在進行

async def chat_handler(websocket):
    global permission_queue

    # 接收用戶名稱
    username = await websocket.recv()   #等待前端輸入名稱
    connected_users[websocket] = username

    # 廣播新用戶加入的消息
    join_message = f"{username} has joined the chat!"
    await broadcast(format_message("Server", join_message))

    board_data = {"Board": [[0 for _ in range(15)] for _ in range(15)]}

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
                    if "player" in data and "row" in data and "row" in data: # 回傳資料為用戶按下的座標
                        socket_player = data["player"]  # 確認當前走棋玩家
                        r = data["row"]
                        c = data["col"]
                        if game.is_valid(r, c):
                            game.make_move(r, c, data["player"])
                            game.log_move(game.board,data["player"],r,c)
                        else:
                            await websocket.send(format_message("Server", "Invalid Move!"))
                            await permission_queue[0].send(json.dumps({"action": "allow"}))
                            continue
                        board_data = {
                            "Board": game.board,  # 使用鍵名 Board 傳遞棋盤給前端用戶
                        }
                        if socket_player != game.current_player:    # 如果不一樣就代表遊戲規則判定換人(定義於make_move函數中)
                            # 權限轉移邏輯
                            permission_queue.append(permission_queue.pop(0))                    

                        await permission_queue[0].send(json.dumps({"action": "allow"}))
                        await broadcast(json.dumps(board_data))  # 將資料轉為 JSON 字串
                        
                        if game.is_win() != 2:  # 遊戲結束
                            game.save_log_to_json()
                            print(f"game over! winner is {game.winner}")
                            await broadcast(format_message("Server", f"game over! winner is {game.winner}"))
                            await broadcast(json.dumps({"Winner": game.winner}))
                            permission_queue = []
                        continue
                    
                except json.JSONDecodeError:
                    pass  # 若訊息不是 JSON 格式，繼續處理為普通訊息

            elif websocket not in permission_queue or websocket != permission_queue[0]:
                # 非權限用戶試圖傳送座標
                try:
                    data = json.loads(message)
                    if "row" in data and "col" in data:
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
        if websocket in permission_queue:   # 此用戶是遊戲玩家
            permission_queue.remove(websocket)
            # 玩家離線且沒有正常結束
            if game.winner == 2:
                game.save_log_to_json()
                game.reset()
                board_data = {
                    "Board": game.board,  # 使用鍵名 Board 傳遞棋盤給前端用戶
                }
                await broadcast(json.dumps(board_data))  # 將資料轉為 JSON 字串

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
    # async with serve(chat_handler, "10.106.38.184", 8765) as server:
    async with serve(chat_handler, "localhost", 8765) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())