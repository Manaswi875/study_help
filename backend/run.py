"""
Development server startup script
"""

import uvicorn
from app import app
from config.settings import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
