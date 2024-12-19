import asyncio
import websockets
import json
import random
from datetime import datetime
import aiohttp  # 新增此模組以便發送 HTTP 請求
from GameLogics.Gomoku import Gomoku_game
from GameLogics.OthelloGame import OthelloGame
from GameLogics.Dots_and_Box import DotsAndBox

# 定義一個字典，映射 GID 到對應的遊戲類別
game_classes = {
    1: lambda: Gomoku_game(19),
    2: lambda: Gomoku_game(15),
    3: lambda: OthelloGame(10),
    4: lambda: DotsAndBox(5,5)
}

GID_path = {
    1: "static/Log/GO_log/",
    2: "static/Log/Gomoku_log/",
    3: "static/Log/Othello_log/",
    4: "static/Log/DaB_log/"
}

# 房間資料結構
rooms = {
    1: {},
    2: {},
    3: {},
    4: {}
}
fighting_users = {
    1: {},
    2: {},
    3: {},
    4: {}
}

def assignPermission(rooms, holder, room_id):
    if holder == rooms[room_id]["users"][0][1]:
        socket = rooms[room_id]["users"][0][0]
    else:
        socket = rooms[room_id]["users"][1][0]
    return socket
    

async def chat_handler(websocket):
    current_room = None
    username = None

    try:
        # 接收 JSON 格式用戶資料
        async for message in websocket:
            
            data = json.loads(message)
            action = data.get("action")
            
            #首次進入房間，顯示目前存在的房間
            if action == "onloadPage":
                GID = int(data["GID"])
                room_id = data["room_id"]
                username = data["User"]
                current_room = room_id
                # 若房間號不存在，則在socket server建立關於此房間的信息
                if room_id not in rooms[GID]:
                    #設定room裡面有什麼東西
                    rooms[GID][room_id] = {
                        "users":[],
                        "visitors":[],
                        "status":None,
                        "board": [],
                        "message":[],
                        "game": game_classes.get(GID, lambda: None)(),  # 默認為 None
                        "winner": 2 # 遊戲進行中
                    }              
                    rooms[GID][room_id]["users"].append((websocket, username))
                    current_room = room_id
                    rooms[GID][room_id]["status"] = 1

                    await broadcast_board_in_room(GID, room_id, rooms[GID][room_id]["game"].board)
                    
                    print(f"{username}創建並加入{room_id}")
                    await broadcast_in_room(GID,current_room, format_message("Server", "display_msg", f"{username} created and joined room {room_id}"))
                else:
                    # 檢查房間當前狀態
                    if rooms[GID][room_id]["status"] == 1:   #裡面只有1位玩家
                        await broadcast_board_in_room(GID, room_id, rooms[GID][room_id]["game"].board)
                        rooms[GID][room_id]["users"].append((websocket, username))
                        

                        rooms[GID][room_id]["status"] = 2
                        
                        # 已確定對戰人員
                        fighting_users[GID][room_id] = [rooms[GID][room_id]["users"][0][1],username]

                         # 先加入的人自動獲得權限
                        fighting_users[GID][current_room].append(0)  #fighting_users[GID][current_room][fighting_users[GID][current_room][2]]有權限
                        permission_holder_idx = fighting_users[GID][current_room][2]
                        permission_holder = fighting_users[GID][current_room][permission_holder_idx]
                        
                        print(f"{username}加入房間{room_id}，開始下棋")
                        await broadcast_in_room(GID, current_room, format_message("Server", "display_msg", f"{username} joined room {room_id}"))

                        # 給權限
                        if len(rooms[GID][room_id]["users"]) > 1:  # 確保至少有兩位玩家
                            permission_socket = assignPermission(rooms[GID], permission_holder, room_id)     
                            await permission_socket.send(format_message("Server","get_location","is your turn"))
                            await broadcast_board_in_room(GID, room_id, rooms[GID][room_id]["game"].board)
                             # 如果需要，先送可走棋給前端
                            if GID == 3:    #黑白棋
                                valids = rooms[GID][room_id]["game"].getValidMoves(rooms[GID][room_id]["game"].current_player)
                                valids_data = {
                                    "action": "get_valids",
                                    "valids": valids,
                                }
                                await permission_socket.send(json.dumps(valids_data))
                                await broadcast_board_in_room(GID, room_id, rooms[GID][room_id]["game"].board)
                        else:
                            print(f"權限未分配，因為房間 {room_id} 目前只有一位玩家")
                    
                    elif rooms[GID][room_id]["status"] == 3 and username in fighting_users[GID][room_id]: #判斷新加入的人是否為先前斷線的人
                        rooms[GID][room_id]["users"].append((websocket, username))
                        await broadcast_board_in_room(GID, room_id, rooms[GID][room_id]["game"].board)
                        print(f"{username}重新加入房間{room_id}，開始下棋")
                        await broadcast_in_room(GID, current_room, format_message("Server", "display_msg", f"{username} rejoined room {room_id}"))
                        
                        # 重新給權限
                        permission_holder_idx = fighting_users[GID][current_room][2]
                        permission_holder = fighting_users[GID][current_room][permission_holder_idx]
                        if permission_holder == username:
                            permission_socket = assignPermission(rooms, permission_holder, room_id)
                            await permission_socket.send(format_message("Server","get_location","is your turn"))
                            await broadcast_board_in_room(GID, room_id, rooms[GID][room_id]["game"].board)
                             # 如果需要，先送可走棋給前端
                            if GID == 3:    #黑白棋
                                valids = rooms[GID][room_id]["game"].getValidMoves(rooms[GID][room_id]["game"].current_player)
                                valids_data = {
                                    "action": "get_valids",
                                    "valids": valids,
                                }
                                await permission_socket.send(json.dumps(valids_data))
                                await broadcast_board_in_room(GID, room_id, rooms[GID][room_id]["game"].board)
                        


                    else:   #當房間已有兩人，其餘人都設為旁觀者
                        await broadcast_board_in_room(GID, room_id, game.board)
                        print(f"{username}作為觀戰者{room_id}")
                        rooms[GID][room_id]["visitors"].append((websocket, username))
                        await broadcast_in_room(GID, current_room, format_message("Server", "display_msg", f"{username}作為觀戰者加入房間{room_id}"))
                    
            # 接收用戶傳送座標
            elif action == "send_coordinates":
                room_id = data["room_id"]
                sender = data["sender"]
                r = data["Row"]
                c = data["Col"]
                coordinate = {
                    "Row": r,
                    "Col": c
                }
                if room_id in rooms[GID] and rooms[GID][room_id]["winner"] == 2:
                    game = rooms[GID][room_id]["game"]
                    swap = False
                    if game.is_valid(r,c):
                        last_player = game.current_player
                        game.make_move(r,c,game.current_player) # 落子
                        
                        await broadcast_board_in_room(GID, room_id, game.board)
                        if last_player == game.current_player:  # 代表沒有換人
                            swap = False
                        else:
                            swap = True
                        formatted_message = format_message(sender,"display_location", coordinate)
                        rooms[GID][room_id]["board"].append(formatted_message)
                        await broadcast_in_room(GID, room_id, formatted_message)

                        winner = game.is_win()
                        rooms[GID][room_id]["winner"] = winner
                        if winner != 2:
                            file_path = GID_path[GID]
                            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                            file_path += f"{current_time}.json"
                            game.save_log_to_json(file_path)
                            result_data= {
                                        "action": "get_result",
                                        "result": winner
                            }
                            await broadcast_in_room(GID, room_id, json.dumps(result_data))
                            if winner == -1:
                                formatted_message =  format_message("Server","display_message", f"遊戲結束! 勝者為{fighting_users[GID][current_room][0]}")
                            elif winner == 0:
                                formatted_message =  format_message("Server","display_message", "遊戲結束! 結果為平手")
                            elif winner == 1:
                                formatted_message =  format_message("Server","display_message", f"遊戲結束! 勝者為{fighting_users[GID][current_room][1]}")
                            await broadcast_in_room(GID, room_id, formatted_message)

                        # 換人邏輯
                        if swap:
                            permission_holder_idx = fighting_users[GID][room_id][2]
                            if len(rooms[GID][room_id]["users"]) > 1:
                                if permission_holder_idx == 0:  # 如果是第一位玩家
                                    fighting_users[GID][room_id][2] = 1  # 換成第二位玩家
                                    web = rooms[GID][room_id]["users"][1][0]  # 給第二位玩家
                                else:  # 如果是第二位玩家
                                    fighting_users[GID][room_id][2] = 0  # 換回第一位玩家
                                    web = rooms[GID][room_id]["users"][0][0]  # 給第一位玩家
                                    
                                await web.send(format_message("Server","get_location","is your turn"))
                                if GID == 3:    #黑白棋
                                    valids = game.getValidMoves(game.current_player)
                                    valids_data = {
                                        "action": "get_valids",
                                        "valids": valids,
                                    }
                                    await web.send(json.dumps(valids_data))
                                    await broadcast_board_in_room(GID, room_id, game.board)
                            else:
                                print(f"房間 {room_id} 玩家不足，無法分配權限")
                        else:
                            await websocket.send(format_message("Server","get_location","is your turn"))
                    else:
                        await broadcast_in_room(GID, room_id, format_message("Server","invalid_move", f"{sender}, that was an invalid move!"))
                        await websocket.send(format_message("Server","get_location","is your turn"))
                        if GID == 3:    #黑白棋
                            await websocket.send(json.dumps(valids_data))
                            await broadcast_board_in_room(GID, room_id, game.board)
                
            # 處理接上前與斷線
            elif action == "close_connection":
                room_id = data["room_id"]
                sender = data["sender"]
                await broadcast_in_room(GID, current_room, format_message("Server", "display_msg", f"{sender} has left the room"))
                # 當有人斷線並且是對戰中的玩家
                if sender in rooms[GID][room_id]["users"][0] or rooms[GID][room_id]["users"][1] and rooms[GID][room_id]["status"] == 2:
                    rooms[GID][room_id]["status"] = 3   # 等待斷線重連
                
                print(f"Action: {action} Room: {room_id} User: {sender}")
            
    except websockets.ConnectionClosed:
        print("Connection closed - except block triggered")
        if current_room and username:
            print(f"{username} left")
            rooms[GID][current_room]["users"].remove((websocket, username))
            if not rooms[GID][current_room]["users"]:
                if current_room in fighting_users[GID]:
                    del fighting_users[GID][current_room]
                # 房間內沒人時刪除房間                
                del rooms[GID][current_room]
                # 發送刪除房間的 DELETE 請求
                async with aiohttp.ClientSession() as session:
                    async with session.delete(f"http://10.106.38.184:8080/delete_room?room_id={current_room}&GID={GID}") as response:
                        if response.status == 200:
                            print(f"Room {current_room} successfully deleted via API")
                        else:
                            print(f"Failed to delete room {current_room} via API")
    
    # 斷線or異常
    finally:
        if current_room and username:
            print(f"{username} left")
            rooms[GID][current_room]["users"].remove((websocket, username))
            if not rooms[GID][current_room]["users"]:
                if current_room in fighting_users[GID]:
                    del fighting_users[GID][current_room]
                # 房間內沒人時刪除房間                
                del rooms[GID][current_room]
                # 發送刪除房間的 DELETE 請求
                async with aiohttp.ClientSession() as session:
                    async with session.delete(f"http://10.106.38.184:8080/delete_room?room_id={current_room}&GID={GID}") as response:
                        if response.status == 200:
                            print(f"Room {current_room} successfully deleted via API")
                        else:
                            print(f"Failed to delete room {current_room} via API")

# 向對應的房間廣播訊息
async def broadcast_in_room(GID, room_id, message):  
    for websocket,_ in rooms[GID][room_id]["users"]:
        await websocket.send(message)

async def broadcast_board_in_room(GID, room_id, board):
    board_data = {
        "action": "get_board",
        "Board": board,  # 使用鍵名 Board 傳遞棋盤給前端用戶
    }
    
    for websocket,_ in rooms[GID][room_id]["users"]:
        await websocket.send(json.dumps(board_data))

# 決定先手是誰
def first_play():
    res = random.randint(1,100) % 2
    return res 
# 傳送格式化訊息
def format_message(sender,action,message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return json.dumps({"timestamp": timestamp, "sender": sender,"action": action, "message": message})

async def main():
    print("WebSocket server is running...")
    async with websockets.serve(chat_handler, "10.106.38.184", 8765):
        await asyncio.Future()  # 永遠運行

if __name__ == "__main__":
    asyncio.run(main())
