import asyncio
import websockets
import json
import random
from datetime import datetime
import aiohttp  # 新增此模組以便發送 HTTP 請求
from GameLogics.Gomoku import Gomoku_game
from GameLogics.OthelloGame import OthelloGame
from GameLogics.Dots_and_Box import DotsAndBox

from Database.Methods import *
IP = "10.106.27.173"
# IP = "192.168.0.133"
# IP = "192.168.2.11"
# 定義一個字典，映射 GID 到對應的遊戲類別

# status = 1: 等待對手加入, 2: 對戰進行中, 3: 一人斷線，等待重新連線, 4: 遊戲結束(雙方斷線or遊戲正常結束)

game_classes = {
    1: lambda: Gomoku_game(19),
    2: lambda: Gomoku_game(15),
    3: lambda: OthelloGame(8),
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

def assignPermission(room, holder, room_id):
    if holder == room[room_id]["users"][0][1]:
        socket = room[room_id]["users"][0][0]
    else:
        socket = room[room_id]["users"][1][0]
    return socket
    

async def chat_handler(websocket):
    current_room = None
    username = None

    try:
        # 接收 JSON 格式用戶資料
        async for message in websocket:
            
            data = json.loads(message)
            action = data.get("action")
            
            # 進入房間
            if action == "onloadPage":
                GID = int(data["GID"])
                room_id = data["room_id"]
                username = data["User"]
                UID = data["UID"]
                current_room = room_id
                # 若房間號不存在，則在socket server建立關於此房間的信息
                if room_id not in rooms[GID]:
                    #設定room裡面有什麼東西
                    rooms[GID][room_id] = {
                        "users":[],     # [(socket, name, UID), ...]
                        "visitors":[],  # [(socket, name, UID), ...]
                        "status":None,  # 1: 1人, 2: 進行中, 3: 進行中斷
                        "board": [],
                        "message":[],
                        "game": game_classes.get(GID, lambda: None)(),  # 默認為 None
                        "winner": 2 ,# 遊戲進行中
                        "BID":""
                    }              
                    rooms[GID][room_id]["users"].append((websocket, username, UID))
                    current_room = room_id
                    rooms[GID][room_id]["status"] = 1
                    # 發送對戰人員給前端
                    players = [username, "N/A"]
                    players_data = {
                        "action": "get_players",
                        "players": players
                    }
                    await broadcast_in_room(GID, room_id, json.dumps(players_data))
                    
                    #顯示版面
                    await broadcast_board_in_room(GID, room_id, rooms[GID][room_id]["game"].board)
                    
                    print(f"{username}創建並加入{room_id}")
                    await broadcast_in_room(GID,current_room, format_message("Server", "display_msg", f"{username} created and joined room {room_id}"))
                else:
                    # 檢查房間當前狀態
                    if rooms[GID][room_id]["status"] == 1:   #裡面只有1位玩家
                        await broadcast_board_in_room(GID, room_id, rooms[GID][room_id]["game"].board)
                        rooms[GID][room_id]["users"].append((websocket, username, UID))
                        
                        # 遊戲正式開始
                        rooms[GID][room_id]["status"] = 2
                        
                        # 已確定對戰人員
                        players = [rooms[GID][room_id]["users"][0][1],username]
                        fighting_users[GID][room_id] = players
                        
                        # 發送對戰人員給前端
                        players_data = {
                            "action": "get_players",
                            "players": players
                        }
                        await broadcast_in_room(GID, room_id, json.dumps(players_data))
                        
                        # 在這邊串接資料庫
                        BID = Generate_BID(GID)
                        rooms[GID][room_id]["BID"] = BID
                        board = {
                            "BoardID":BID,
                            "GameID":GID,
                            "Steps":"temp",
                            "State":2
                        }
                        # 建立新的Board data, BID="新BID", GameID=GID, state=2, steps=None (steps檔案為存檔，先列為空，確定存檔在儲存)
                        Create_Data("Boards",board)
                        # 建立新的UB data, Player1=rooms[GID][room_id]["users"][0][2], Player2=rooms[GID][room_id]["users"][1][2], BID=BID
                        ub = {
                            "BoardID":BID,
                            "Player1":rooms[GID][room_id]["users"][0][2],
                            "Player2":rooms[GID][room_id]["users"][1][2]
                        }
                        Create_Data("UB",ub) 
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
                        
                        rooms[GID][room_id]["status"] == 2  # 人回來了，繼續進行對弈
                        
                        rooms[GID][room_id]["users"].append((websocket, username,UID))
                        await broadcast_board_in_room(GID, room_id, rooms[GID][room_id]["game"].board)
                        print(f"{username}重新加入房間{room_id}，開始下棋")
                        
                        players_data = {
                            "action": "get_players",
                            "players": fighting_users[GID][room_id][:2]
                        }
                        await broadcast_in_room(GID, room_id, json.dumps(players_data))
                        
                        await broadcast_in_room(GID, current_room, format_message("Server", "display_msg", f"{username} rejoined room {room_id}"))
                        
                        # 重新給權限
                        permission_holder_idx = fighting_users[GID][current_room][2]
                        permission_holder = fighting_users[GID][current_room][permission_holder_idx]
                        if permission_holder == username:
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
                        
                    else:   #當房間已有兩人，其餘人都設為旁觀者
                        # 告知觀戰目前對弈玩家
                        players_data = {
                            "action": "get_players",
                            "players": fighting_users[GID][room_id][:2]
                        }
                        await broadcast_in_room(GID, room_id, json.dumps(players_data))
                        
                        await broadcast_board_in_room(GID, room_id, rooms[GID][room_id]["game"].board)
                        print(f"{username}作為觀戰者加入{room_id}")
                        rooms[GID][room_id]["visitors"].append((websocket, username,UID))
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
                        
                        # 遊戲結束
                        if winner != 2:
                            file_path = GID_path[GID]
                            # file_path要改成BID
                            BID = rooms[GID][room_id]["BID"]
                            file_name = f"{BID}.json"
                            file_path += file_name
                            
                            # 串資料庫，存結果
                            # 確認存檔完成，資料庫: Board[BID][steps] = file_path
                            # 存下遊戲結果，資料庫: Board[BID][state] = winner
                            Update_Table("Boards",{"Steps":file_path,"State":winner},{"BoardID":BID})
                            
                            # 資料庫: 先手玩家: UID1: rooms[GID][room_id]["users"][0][2]
                            # 資料庫: 後手玩家: UID2: rooms[GID][room_id]["users"][1][2]
                            
                            game.save_log_to_json(file_path)
                            print("遊戲結束，存檔")   
                            result_data= {
                                        "action": "get_result",
                                        "result": winner
                            }
                            await broadcast_in_room(GID, room_id, json.dumps(result_data))
                            if winner == -1:
                                # 資料庫 Record:
                                # 先手勝 
                                RID = f'{GID}_{rooms[GID][room_id]["users"][0][2]}'
                                rows = Get_Records(RID,['Win','Total'])
                                print(RID,rows)
                                # Record[UserID = UID1][GameID = GID][Win] += 1
                                # Record[UserID = UID1][GameID = GID][Total] += 1
                                data = {
                                    "Win":rows[0][0] +1,
                                    "Total":rows[0][1] +1
                                }
                                print(data)
                                Update_Table("Records",data,{"RecordID":RID})
                                # Record[UserID = UID2][GameID = GID][Lose] += 1
                                # Record[UserID = UID1][GameID = GID][Total] += 1
                                RID = f'{GID}_{rooms[GID][room_id]["users"][1][2]}'
                                rows = Get_Records(RID,['Lose','Total'])
                                data = {
                                    "Lose":rows[0][0] +1,
                                    "Total":rows[0][1] +1
                                }
                                Update_Table("Records",data,{"RecordID":RID})
                                
                                rooms[GID][room_id]["status"] = 4
                                formatted_message =  format_message("Server","display_message", f"遊戲結束! 勝者為{fighting_users[GID][current_room][0]}")
                            elif winner == 0:
                                # 資料庫 Record:
                                # 平手 
                                # Record[UserID = UID1][GameID = GID][Draw] += 1
                                # Record[UserID = UID1][GameID = GID][Total] += 1
                                RID = f'{GID}_{rooms[GID][room_id]["users"][0][2]}'
                                rows = Get_Records(RID,['Draw','Total'])
                                data = {
                                    "Draw":rows[0][0] +1,
                                    "Total":rows[0][1] +1
                                }
                                Update_Table("Records",data,{"RecordID":RID})
                                
                                # Record[UserID = UID2][GameID = GID][Draw] += 1
                                # Record[UserID = UID1][GameID = GID][Total] += 1
                                RID = f'{GID}_{rooms[GID][room_id]["users"][1][2]}'
                                rows = Get_Records(RID,['Draw','Total'])
                                data = {
                                    "Draw":rows[0][0] +1,
                                    "Total":rows[0][1] +1
                                }
                                Update_Table("Records",data,{"RecordID":RID})
                                rooms[GID][room_id]["status"] = 4
                                formatted_message =  format_message("Server","display_message", "遊戲結束! 結果為平手")
                            elif winner == 1:
                                # 後手勝
                                formatted_message =  format_message("Server","display_message", f"遊戲結束! 勝者為{fighting_users[GID][current_room][1]}")
                                
                                RID = f'{GID}_{rooms[GID][room_id]["users"][1][2]}'
                                rows = Get_Records(RID,['Win','Total'])
                                # Record[UserID = UID1][GameID = GID][Win] += 1
                                # Record[UserID = UID1][GameID = GID][Total] += 1
                                data = {
                                    "Win":rows[0][0] +1,
                                    "Total":rows[0][1] +1
                                }
                                print(data)
                                Update_Table("Records",data,{"RecordID":RID})
                                # Record[UserID = UID2][GameID = GID][Lose] += 1
                                # Record[UserID = UID1][GameID = GID][Total] += 1
                                RID = f'{GID}_{rooms[GID][room_id]["users"][0][2]}'
                                rows = Get_Records(RID,['Lose','Total'])
                                data = {
                                    "Lose":rows[0][0] +1,
                                    "Total":rows[0][1] +1
                                }
                                Update_Table("Records",data,{"RecordID":RID})
                                rooms[GID][room_id]["status"] = 4
                                
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
                # 當有人斷線並且是對戰中的玩家且狀態為對戰中
                if sender in rooms[GID][room_id]["users"][0] or rooms[GID][room_id]["users"][1] and rooms[GID][room_id]["status"] == 2:
                    rooms[GID][room_id]["status"] = 3   # 等待斷線重連
                
                print(f"Action: {action} Room: {room_id} User: {sender}")
            
    except websockets.ConnectionClosed:
        print("Connection closed - except block triggered")
        pass
    
    # 斷線or異常
    finally:
        if current_room and username:
            print(f"{username} left")


            # if rooms[GID][room_id]["status"] == 2:
            
            # 判斷離開者並移除rooms結構移除
            if (websocket, username,UID) in rooms[GID][current_room]["users"]:
                rooms[GID][current_room]["users"].remove((websocket, username, UID))
            elif (websocket, username, UID) in rooms[GID][current_room]["visitors"]:
                rooms[GID][current_room]["visitors"].remove((websocket, username, UID))
            
            # 房間內對戰的玩家均離開時
            if not rooms[GID][current_room]["users"]:
                
                if current_room in fighting_users[GID]:
                    del fighting_users[GID][current_room]
            
                if rooms[GID][room_id]["status"] == 3:
                    rooms[GID][room_id]["status"] = 4   # 斷線，且僅存玩家也離開，宣告結束
                    # file_path要改成路徑+BID
                    BID = rooms[GID][room_id]["BID"]
                    file_name = f"{BID}.json"
                    file_path += file_name
                    
                    Update_Table("Boards",{"Steps":file_path,"State":3},{"BoardID":BID})
                    
                    RID = f'{GID}_{rooms[GID][room_id]["users"][0][2]}'
                    rows = Get_Records(RID,['Unfinish','Total'])
                    data = {
                        "Unfinish":rows[0][0] +1,
                        "Total":rows[0][1] +1
                    }
                    Update_Table("Records",data,{"RecordID":RID})
                    
                    # Record[UserID = UID2][GameID = GID][Unfinish] += 1
                    # Record[UserID = UID1][GameID = GID][Total] += 1
                    RID = f'{GID}_{rooms[GID][room_id]["users"][1][2]}'
                    rows = Get_Records(RID,['Unfinish','Total'])
                    data = {
                        "Unfinish":rows[0][0] +1,
                        "Total":rows[0][1] +1
                    }
                    Update_Table("Records",data,{"RecordID":RID})
                    rooms[GID][current_room]["game"].save_log_to_json(file_path)
                    print("中離存檔")    
                
                # 房間內沒人時刪除房間                
                del rooms[GID][current_room]
                # 發送刪除房間的 DELETE 請求
                async with aiohttp.ClientSession() as session:
                    async with session.delete(f"http://{IP}:8080/delete_room?room_id={current_room}&GID={GID}") as response:
                        if response.status == 200:
                            print(f"Room {current_room} successfully deleted via API")
                        else:
                            print(f"Failed to delete room {current_room} via API")

# 向對應的房間廣播訊息
async def broadcast_in_room(GID, room_id, message):  
    for websocket,_, UID in rooms[GID][room_id]["users"]:
        await websocket.send(message)
    if rooms[GID][room_id]["visitors"]:
        for websocket,_ in rooms[GID][room_id]["visitors"]:
            await websocket.send(message)
    

async def broadcast_board_in_room(GID, room_id, board):
    board_data = {
        "action": "get_board",
        "Board": board,  # 使用鍵名 Board 傳遞棋盤給前端用戶
    }
    
    for websocket,_,UID in rooms[GID][room_id]["users"]:
        await websocket.send(json.dumps(board_data))
    if rooms[GID][room_id]["visitors"]:
        for websocket,_ in rooms[GID][room_id]["visitors"]:
            await websocket.send(json.dumps(board_data))
# 決定先手是誰
def first_play():
    res = random.randint(1,100) % 2
    return res 
# 傳送格式化訊息
def format_message(sender,action,message):
    return json.dumps({"sender": sender,"action": action, "message": message})

async def main():
    print("WebSocket server is running...")
    async with websockets.serve(chat_handler, IP, 8765):
        await asyncio.Future()  # 永遠運行

if __name__ == "__main__":
    asyncio.run(main())
