#!/usr/bin/env python3
"""
Main entry point for the K-Square Onboarding Application.
This file serves as the root-level entry point that imports the FastAPI app from the backend module.
"""

from backend.main import app

# Re-export the app for uvicorn to find
__all__ = ['app']

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )