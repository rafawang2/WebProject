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

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

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

# 設定圖片儲存的目錄
UPLOAD_DIR = Path("static/images")  # 改為相對路徑
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # 如果目錄不存在則創建
@app.get("/profile", response_class=HTMLResponse)
async def profilepage(request: Request):
    return templates.TemplateResponse("user_profile.html", {"request": request, "time": current_time})

# 上傳圖片，將其儲存為 man.png 並返回 URL
@app.post("/upload/")
async def upload_image(image: UploadFile = File(...)):
    try:
        # 獲取圖片的文件名，並儲存為 man.png
        file_location = UPLOAD_DIR / "man.png"
        with open(file_location, "wb") as f:
            f.write(await image.read())  # 儲存圖片到伺服器

        # 返回儲存的圖片的 URL
        return JSONResponse(content={"success": True, "image_url": f"/static/images/man.png"})
    except Exception as e:
        return JSONResponse(content={"success": False, "error": str(e)}, status_code=500)

# 提供靜態文件的路由，讓圖片可以被訪問
@app.get("/static/images/man.png")
async def get_image():
    file_location = UPLOAD_DIR / "man.png"
    if file_location.exists():
        return FileResponse(file_location)
    return JSONResponse(content={"error": "File not found"}, status_code=404)


if __name__ == "__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8080,reload=True)