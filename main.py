import uvicorn, json
from pydantic import BaseModel
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from datetime import datetime
current_time = datetime.now().timestamp()
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

class BoardSelection(BaseModel):
    BID: int
    GID: int
    status: int
    player1: str
    player2: str

@app.get("/",response_class=HTMLResponse)
async def gotohome(request: Request):
    # 導向到 /home
    return RedirectResponse(url="/home")

@app.get("/home",response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("Home.html",{"request": request , "time": current_time})

@app.get("/about",response_class=HTMLResponse)
async def aboutpage(request: Request):
    return templates.TemplateResponse("about.html",{"request": request , "time": current_time})

@app.get("/SelectReplayBoard",response_class=HTMLResponse)
async def SelectPeplay(request: Request):
    return templates.TemplateResponse("SelectReplayBoard.html", {"request": request, "time": current_time})



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



if __name__ == "__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8080,reload=True)