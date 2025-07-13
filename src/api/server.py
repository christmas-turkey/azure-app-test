import os
import uvicorn
from fastapi import FastAPI
from src.api.routes.employees import router as employees_router
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="Employees API", version="1.0.0")

# Register routers
app.include_router(employees_router)


if __name__ == "__main__":
    uvicorn.run("src.api.server:app", host=os.getenv("HOST"), port=int(os.getenv("PORT")), reload=True)