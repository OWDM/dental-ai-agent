"""Services module (database, calendar, email)"""
from .database import get_database, DatabaseService
from .calendar import get_calendar, CalendarService

__all__ = ["get_database", "DatabaseService", "get_calendar", "CalendarService"]
