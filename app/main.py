from fastapi import FastAPI
from app.routers.auth_router import router as auth_router
from app.routers.job_router import router as job_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(job_router)

@app.get("/")
def home():
    return {
        "message": "AI Job Recommendation System"
    }