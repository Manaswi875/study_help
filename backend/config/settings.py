"""
Configuration management for Adaptive Study Planner
"""

from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Adaptive Study Planner"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str
    db_echo: bool = False
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google Calendar API
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: Optional[str] = None
    google_scopes: str = "https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/calendar.events"
    
    # Notion API
    notion_client_id: Optional[str] = None
    notion_client_secret: Optional[str] = None
    notion_redirect_uri: Optional[str] = None
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Email
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None
    
    # Frontend
    frontend_url: str = "http://localhost:3000"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # Features
    enable_google_calendar: bool = True
    enable_notion: bool = True
    enable_email_notifications: bool = True
    
    # Scheduling
    default_planning_horizon_days: int = 7
    nightly_replan_hour: int = 2
    auto_sync_interval_min: int = 15
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
