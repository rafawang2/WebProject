import uvicorn, json
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pathlib import Path
from datetime import datetime

from GameLogics.OthelloGame import OthelloGame
from GameLogics.bots.AlphaBetaOthello import OthelloAlphaBeta
from GameLogics.Dots_and_Box import DotsAndBox
from GameLogics.bots.DaB_MCTS import MCTSPlayer
from Database.Methods import *

current_time = datetime.now().timestamp()
app = FastAPI()

#伺服器資源檔案
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

#根目錄，導向首頁
@app.get("/",response_class=HTMLResponse)
async def gotoLogin(request: Request):
    # 導向到 /login
    return RedirectResponse(url="/login")

@app.get("/login",response_class=HTMLResponse)
async def loginPage(request: Request):
    return templates.TemplateResponse("login.html",{"request": request , "time": current_time})


#首頁，渲染首頁畫面(Home.html)
@app.get("/home",response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("Home.html",{"request": request , "time": current_time})

#關於頁面
@app.get("/about",response_class=HTMLResponse)
async def aboutpage(request: Request):
    return templates.TemplateResponse("about.html",{"request": request , "time": current_time})



def save_replay_boards_to_json(BIDs, UID):
    """
    將 BIDs 字典保存為指定格式的 JSON 文件。

    :param BIDs: 包含對局資訊的字典
    :param filename: 儲存的 JSON 文件名稱（默認為 "replay_boards.json"）
    """
    filename = f'static/Log/Replay_log/ReplayBoard_log_{UID}.json'
    # 包裝 ReplayBoards 結構
    data = {"ReplayBoards": BIDs}
    
    # 將資料寫入 JSON 文件
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"JSON file saved successfully as {filename}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")

@app.get("/get_replay_BIDs")
async def get_user_historyBIDs(request: Request):
    # 資料庫
    UID = request.headers.get("UID")
    #資料庫
    # 這邊取得UID裡面的所有BID紀錄，並存成dict list
    replay_data = Get_Replay(UID)
    save_replay_boards_to_json(replay_data,UID)
    
    return replay_data

@app.get("/SelectReplayBoard",response_class=HTMLResponse)
async def SelectPeplay(request: Request):
    return templates.TemplateResponse("SelectReplayBoard.html", {"request": request, "time": current_time})

#導向選擇的棋盤頁面，並用BID與GID作為連結參數使用
@app.get("/SelectReplayBoard/replayBoard",response_class=HTMLResponse)
async def replayBoard(request: Request, BID: str, UID: str):
    file_name = f'static/Log/Replay_log/ReplayBoard_log_{UID}.json'
    # 讀取UID 回放盤面 JSON 文件並轉換為 Python 字典
    with open(file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    board = data["ReplayBoards"].get(str(BID))
    state = board["state"]
    p1 = board["player1"]
    p2 = board["player2"]
    GID = board["GID"]
    return templates.TemplateResponse("Replay.html", {  #將此局參數回傳給Replay.html並顯示
        "BID":     BID,
        "GID":     GID,
        "status":  state,
        "player1": p1,
        "player2": p2,
        "request": request,
        "time":    current_time
    })

# 設定圖片儲存的目錄
UPLOAD_DIR = Path("static/images/users")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # 如果目錄不存在則創建

def save_record_to_json(Record_data, UID):
    filename = f'static/Log/GameRecord_log/Record_{UID}.json'
    data = {"record": Record_data}
    # 將資料寫入 JSON 文件
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"JSON file saved successfully as {filename}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")

#渲染個人資料頁面
@app.get("/profile", response_class=HTMLResponse)
async def profilepage(request: Request, UID: str):
    
    record_data = {}
    for i in range(1,5):
        data  = Get_Records(f'{i}_{UID}',['Total','Win','Lose','Draw','Unfinish'])
        record_data[i]={
            "total": data[0][0],
            "win": data[0][1],
            "lose": data[0][2],
            "draw": data[0][3],
            "unfinish": data[0][4]  
        }
    save_record_to_json(record_data, UID)
    return templates.TemplateResponse("user_profile.html", {"request": request, "time": current_time})

#上傳圖片，將其儲存為 man.png 並返回 URL
@app.post("/upload/")
async def upload_image(image: UploadFile = File(...)):
    try:
        # 獲取圖片的文件名，並儲存為 man.png
        file_location = UPLOAD_DIR / "man.png"
        with open(file_location, "wb") as f:
            f.write(await image.read())  # 儲存圖片到伺服器

        # 返回儲存的圖片的 URL
        return JSONResponse(content={"success": True, "image_url": f"/static/images/users/man.png"})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


exist_rooms = {
    1: [],
    2: [],
    3: [],
    4: []
}

# /selectRoom?GID={GID}
@app.get("/selectRoom", response_class=HTMLResponse)
async def SelectRoom(request: Request, GID: int):
    return templates.TemplateResponse("room_select.html", {"request": request,
                                                           "time": current_time,
                                                           "room_ids": exist_rooms[GID],
                                                           "GID": str(GID)
                                                           })
# 創建房間的API
# /create_room
@app.post("/create_room")
async def create_room(request: Request):
    room_id = request.headers.get("room_id")
    GID = int(request.headers.get("GID"))
    if room_id and room_id not in exist_rooms[GID]:
        # 記錄房間的創建時間
        exist_rooms[GID].append(room_id)
        return {"success": True, "room_ids":exist_rooms[GID]}
    elif room_id in exist_rooms[GID]:
        return {"success": False, "message": "The room already exists!"}
    else:
        return {"success": False, "message": "room_id not provided"}


# 將當前login的user的名字存入user_data 
@app.post("/save_name")
async def save_name(request: Request):
    user_name = request.headers.get("username")
    if not user_name:
        return JSONResponse(content={"success": False, "error": "Username is required"})
    
    # 資料庫串接: 檢查user_name是否在資料庫，如果在，回傳username對應的UID，如果不在就建立新的User跟Record
    UID = Check_Username(user_name)
    return JSONResponse(content={"success": True, "UID": UID}) 


# 刪除房間的API
# /delete_room?room_id={room_id}&GID={GID}
@app.delete("/delete_room")
async def delete_room(room_id: str, GID: int):
    if room_id in exist_rooms[GID]:
        exist_rooms[GID].remove(room_id)
        print(exist_rooms)
        return {"success": True, "message": f"Room {room_id} has been deleted."}
    else:
        return {"success": False, "message": "Room not found!"}

# 房間頁面
# /room?room_id={room_id}&GID={GID}
@app.get("/room")
async def room_page(request: Request, room_id: str, GID: int):
    if room_id not in exist_rooms[GID]:
        return {"error": "Room not found!"}
    
    return templates.TemplateResponse("room.html", {
        "request": request,
        "time": current_time,
        "room_id": room_id,
        "GID": str(GID)
        })

# 遊戲介面
@app.get("/playGame",response_class=HTMLResponse)
async def replayBoard(request: Request, GID: int):  
    return templates.TemplateResponse("PlayGame.html", {  #將此局參數回傳給Replay.html並顯示
        "GID":     GID,
        "request": request,
        "time":    current_time
    })


bot_games = {}
# 與AI機器人的對下的API
@app.get("/bot_room")
async def room_page(request: Request, UID: str, GID: int):
    if UID not in bot_games:
        if GID == 1:
            bot_games[UID] = OthelloGame(8)
        elif GID == 2:
            bot_games[UID] = OthelloGame(8)
        elif GID == 3:
            bot_games[UID] = OthelloGame(8)
        elif GID == 4:
            bot_games[UID] = DotsAndBox(5,5)
    
    return templates.TemplateResponse("bot_room.html", {
        "request": request,
        "time": current_time,
        "GID": str(GID),
        "board": bot_games[UID].board
        })

@app.get("/get_board")
async def get_board(request: Request, UID: str, GID: int):
    permission = ""
    if bot_games[UID].current_player == -1:
        permission = "Human"
    else:
        permission = "BOT"
    if bot_games[UID].is_win()!=2:
        permission = "No"
    return {"board": bot_games[UID].board, "Permission": permission, "valid_moves": bot_games[UID].getValidMoves(bot_games[UID].current_player), "winner": bot_games[UID].winner}


@app.get("/get_bot_move")
async def get_bot_move(request: Request, UID: str, GID: int):
    # bot下的座標
    if GID == 1:
        r, c = OthelloAlphaBeta().getAction(bot_games[UID].board, bot_games[UID].current_player)
    elif GID == 2:
        r, c = OthelloAlphaBeta().getAction(bot_games[UID].board, bot_games[UID].current_player)
    elif GID == 3:
        r, c = OthelloAlphaBeta().getAction(bot_games[UID].board, bot_games[UID].current_player)
    elif GID == 4:
        r, c = MCTSPlayer(num_simulations=50, exploration_weight=1.5, max_depth=3,game=bot_games[UID]).getAction(bot_games[UID].board, bot_games[UID].current_player)
    permission = "BOT"
    if bot_games[UID].current_player==1:
        last_player = bot_games[UID].current_player
        bot_games[UID].make_move(r,c, bot_games[UID].current_player)
        bot_games[UID].winner = bot_games[UID].is_win()
            
        # 結束遊戲
        if bot_games[UID].winner != 2:
            end_board = bot_games[UID].board
            winner = bot_games[UID].winner
            del bot_games[UID]
            return {"board": end_board, "winner": winner, "permission": "No"}

        if last_player != bot_games[UID].current_player:    # 換成玩家
            permission = "Human"
        else:
            permission = "BOT"    # 沒換人
    # 返回新的board
    msg = {
        "sender": "BOT",
        "message": f"{r} {c}"
    }
    valids = bot_games[UID].getValidMoves(bot_games[UID].current_player)
    return {"board": bot_games[UID].board, "valid_moves": valids, "permission": permission, "winner": bot_games[UID].winner, "message": msg}

@app.post("/user_send_coordinate")
async def handle_coordinate(request: Request, UID: str):
    # user下的座標
    r = int(request.headers.get("row"))
    c = int(request.headers.get("col"))
    permission = "Human"
    if bot_games[UID].is_valid(r,c) and bot_games[UID].current_player==-1:
        last_player = bot_games[UID].current_player
        bot_games[UID].make_move(r,c, bot_games[UID].current_player)
        bot_games[UID].winner = bot_games[UID].is_win()
            
        # 結束遊戲
        if bot_games[UID].winner != 2:
            end_board = bot_games[UID].board
            winner = bot_games[UID].winner
            del bot_games[UID]
            return {"board": end_board, "winner": winner, "permission": "No"}

        if last_player != bot_games[UID].current_player:    # 換成AI
            permission = "BOT"
        else:
            permission = "Human"    # 沒換人
    # 返回新的 board
    valids = bot_games[UID].getValidMoves(bot_games[UID].current_player)
    return {"board": bot_games[UID].board, "valid_moves": valids, "permission": permission, "winner": bot_games[UID].winner}
        
if __name__ == "__main__":
    # IP = "26.136.58.171"    #ncnu wifi
    # IP = "192.168.0.133"    #澤生居 wifi
    IP = "26.28.2.92"
    # IP = "192.168.2.11"
    # IP = 127.0.0.1
    uvicorn.run("main:app",host=IP,port=8080,reload=True)