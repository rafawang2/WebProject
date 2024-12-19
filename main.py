import uvicorn, json
from pydantic import BaseModel
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pathlib import Path
from datetime import datetime
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

@app.get("/SelectReplayBoard",response_class=HTMLResponse)
async def SelectPeplay(request: Request):
    return templates.TemplateResponse("SelectReplayBoard.html", {"request": request, "time": current_time})

#導向選擇的棋盤頁面，並用BID與GID作為連結參數使用
@app.get("/SelectReplayBoard/replayBoard",response_class=HTMLResponse)
async def replayBoard(request: Request, BID: int, GID: int):
    file_name = 'static/Log/Replay_log/ReplayBoard_log.json'
    # 讀取 JSON 文件並轉換為 Python 字典
    with open(file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    #查找BID，之後由資料庫查找代替
    board = data["ReplayBoards"].get(str(BID))
    status = board["status"]
    p1 = board["player1"]
    p2 = board["player2"]
    
    return templates.TemplateResponse("Replay.html", {  #將此局參數回傳給Replay.html並顯示
        "BID":     BID,
        "GID":     GID,
        "status":  status,
        "player1": p1,
        "player2": p2,
        "request": request,
        "time":    current_time
    })

# 設定圖片儲存的目錄
UPLOAD_DIR = Path("static/images/users")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # 如果目錄不存在則創建

#渲染個人資料頁面
@app.get("/profile", response_class=HTMLResponse)
async def profilepage(request: Request):
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


# 用於保存使用者名稱（簡單模擬存儲）
class NameRequest(BaseModel):
    name: str
user_data = {"name": ""}
# # 保存使用者名稱 API
# @app.post("/save_name")
# async def save_name(request: NameRequest):
#     try:
#         user_data["name"] = request.name  # 從請求中獲取名稱
#         print(user_data["name"])
#         return JSONResponse(content={"success": True, "name": request.name})
#     except Exception as e:
#         return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)


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

if __name__ == "__main__":
    # IP = "10.106.38.184"  #ncnu wifi
    IP = "192.168.0.133"    #澤生居 wifi
    uvicorn.run("main:app",host=IP,port=8080,reload=True)