from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import commutes as commutes

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

app.include_router(commutes.router)

@app.get("/")
async def main():
    return "Mo was here"

def main():
    uvicorn.run(app, host="localhost", port=8000)

if __name__ == "__main__":
    main()
