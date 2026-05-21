from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers.auth_router import router as auth_router
from app.routers.job_router import router as job_router
from app.routers.review_router import router as review_router
from app.routers.matching_router import router as matching_router
from app.routers.crawler_router import router as crawler_router
from app.routers.notification_router import router as notification_router
import asyncio
from app.services.matching_service import run_background_matching

app = FastAPI(
    title="AI Job Recommendation System",
    description="Backend API với JWT Authentication - Quốc's Work",
    version="2.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True
    }
)

@app.on_event("startup")
async def startup_event():
    # Start background matching task
    asyncio.create_task(run_background_matching())

# CORS middleware - cho phép frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(job_router, prefix="/api", tags=["Jobs"])
app.include_router(review_router, prefix="/api", tags=["Reviews"])
app.include_router(matching_router, prefix="/api", tags=["Matching"])
app.include_router(crawler_router, prefix="/api", tags=["Crawler"])
app.include_router(notification_router, prefix="/api", tags=["Notifications"])

# Serve static files (HTML, CSS, JS)
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/js", StaticFiles(directory="js"), name="js")
app.mount("/html", StaticFiles(directory="html"), name="html")

@app.get("/")
def home():
    return {
        "message": "AI Job Recommendation System"
    }