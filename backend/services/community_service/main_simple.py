"""
Simplified Community Service for Testing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="MantraPath Community Service",
    description="Psychology-based community management - Testing Version",
    version="2.0.0-test"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "community-service",
        "version": "2.0.0-test",
        "message": "Clean community service structure implemented successfully!"
    }

@app.get("/")
async def root():
    return {
        "message": "MantraPath Community Service",
        "features": [
            "Psychology-based color themes",
            "Unified community experience", 
            "Personalized feeds",
            "Crisis detection",
            "Calming interactions",
            "Mood-responsive UI"
        ],
        "organization": {
            "models": "Clean database models in models/",
            "services": "Business logic in services/",
            "utils": "Psychology utilities in utils/",
            "config": "Psychology configuration in config/"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
