import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Initialize the FastAPI app
app = FastAPI(
    title="AQI Digital Twin Backend",
    description="Backend API for Air Quality Monitoring System",
    version="1.0.0"
)

# --- CORS SETUP ---
# This is crucial for Hackathons. It allows your React Frontend (running on port 5173)
# to talk to this Python Backend (running on port 8000) without security errors.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (good for dev/hackathons)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],
)

# --- LOGGING SETUP ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- BASIC ROUTES ---

@app.get("/")
async def root():
    """
    Health check endpoint to ensure the server is running.
    """
    return {
        "status": "online",
        "message": "AQI Backend is running successfully!",
        "service": "Digital Twin AQI Monitor"
    }

if __name__ == "__main__":
    # Run the server on localhost:8000
    # reload=True means the server restarts automatically when you save code changes
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)