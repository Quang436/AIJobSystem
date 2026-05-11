from fastapi import FastAPI
from app.routers.auth_router import router as auth_router
from app.routers.job_router import router as job_router

app = FastAPI(
    title="AI Job Recommendation System",
    description="Backend API với JWT Authentication - Quốc's Work",
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True
    }
)

app.include_router(auth_router)
app.include_router(job_router)

@app.get("/")
def home():
    return {
        "message": "AI Job Recommendation System"
    }