import sys
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

sys.path.append(os.getcwd())
from routers import commutes, schedule, user, car_model

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(commutes.router)
app.include_router(schedule.router)
app.include_router(user.router)
app.include_router(car_model.router)


@app.get("/")
async def main():
    """Render a welcome message."""
    return "Welcome to the Chargify API"


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
