"""
Hugging Face Spaces Entry Point

This file is required by Hugging Face Spaces.
It imports and runs the FastAPI backend application.

Hugging Face Spaces automatically:
- Detects this file and starts the application
- Runs on port 7860
- Provides public HTTPS URL
- Handles SSL/TLS
"""

import os
import sys

# Add backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_path)

# Import the FastAPI app
from main import app

# Export for Hugging Face Spaces
if __name__ == "__main__":
    import uvicorn

    # Hugging Face Spaces uses port 7860
    port = int(os.getenv("PORT", "7860"))

    # Run the application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
    )
