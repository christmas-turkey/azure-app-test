import uvicorn
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return '<h1 style="color: red;">Hello Azure!</h1>'


if __name__ == "__main__":
    uvicorn.run("server:app", host=os.getenv("HOST"), port=int(os.getenv("PORT")), reload=True)
