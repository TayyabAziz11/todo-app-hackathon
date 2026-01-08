from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.config import settings
from app.database import engine  # ✅ FIXED: Changed from app.db to app.database

# 👇 IMPORTANT: import models so SQLModel knows about them
from app.models.user import User
from app.models.todo import Todo  # if you have this

from app.routers.auth import router as auth_router
from app.routers.todos import router as todos_router

app = FastAPI(
    title="Todo API",
    version="2.0.0",
    description="Phase II: Multi-user Todo Application with Authentication"
)

# 🔥 CREATE TABLES ON STARTUP
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Register routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(todos_router, prefix="/api", tags=["Todos"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
