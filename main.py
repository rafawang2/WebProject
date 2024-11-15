import uvicorn
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

# 將得到的BID及GID丟到Replay.html
replay_board_type = {"BID":0, "GID":0}

def get_board_type(BID, GID):
    replay_board_type["BID"] = BID
    replay_board_type["GID"] = GID
    
@app.post("/SelectReplayBoard",response_class=HTMLResponse)
async def SelectReplayBoard_post(selection: BoardSelection, request: Request):
    get_board_type(selection.BID, selection.GID)
    print(f"/SelectReplayBoard/replayBoard?BID={replay_board_type['BID']}&GID={replay_board_type['GID']}")
    return templates.TemplateResponse("SelectReplayBoard.html", {"request": request, "time": current_time})
    
@app.get("/SelectReplayBoard/replayBoard",response_class=HTMLResponse)
async def replayBoard(request: Request):
    return templates.TemplateResponse("Replay.html", {
        "BID": replay_board_type["BID"],
        "GID": replay_board_type["GID"],
        "request": request,
        "time": current_time
    })



if __name__ == "__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8080,reload=True)