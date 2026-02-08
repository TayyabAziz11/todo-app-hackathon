"""
Analytics Service - Phase V.1 Skeleton
Microservice for metrics aggregation and insights
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Analytics Service",
    description="Microservice for analytics and insights",
    version="1.0.0"
)

@app.get("/health/ready")
async def readiness_probe():
    return JSONResponse(
        status_code=200,
        content={"status": "ready", "service": "analytics-service"}
    )

@app.get("/health/live")
async def liveness_probe():
    return JSONResponse(
        status_code=200,
        content={"status": "alive", "service": "analytics-service"}
    )

@app.get("/")
async def root():
    return {
        "service": "analytics-service",
        "version": "1.0.0",
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
