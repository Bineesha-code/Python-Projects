#!/usr/bin/env python3
"""
Script to run the FastAPI backend server
"""
import uvicorn
from config import HOST, PORT

if __name__ == "__main__":
    print("🚀 Starting Smart Resume Parser Backend...")
    print(f"📍 Server will be available at: http://{HOST}:{PORT}")
    print(f"📚 API Documentation: http://{HOST}:{PORT}/docs")
    print("🔄 Auto-reload enabled for development")
    print("-" * 50)
    
    uvicorn.run(
        "backend.api.main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    )
