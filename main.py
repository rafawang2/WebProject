import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/styles", StaticFiles(directory="styles"), name="styles")
app.mount("/scripts", StaticFiles(directory="scripts"), name="scripts")
app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/components", StaticFiles(directory="components"), name="components")

templates = Jinja2Templates(directory="templates")

@app.get("/home",response_class=HTMLResponse)
async def homepage(request: Request):
    return templates.TemplateResponse("Home.html",{"request": request})


@app.get("/about",response_class=HTMLResponse)
async def aboutpage(request: Request):
    return templates.TemplateResponse("about.html",{"request": request})




if __name__ == "__main__":
    uvicorn.run("main:app",host="127.0.0.1",port=8080,reload=True)