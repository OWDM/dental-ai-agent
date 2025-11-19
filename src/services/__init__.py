"""Services module (database, calendar, email)"""
from .database import get_database, DatabaseService

__all__ = ["get_database", "DatabaseService"]
