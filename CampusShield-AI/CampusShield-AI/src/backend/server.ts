import fastapi
from fastapi.middleware.cors import CORSMiddleware
from api import index

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(index.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}