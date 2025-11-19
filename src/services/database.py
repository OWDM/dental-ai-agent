"""
Database Service - Supabase Client
Provides simple functions to query the database
"""

from supabase import create_client, Client
from src.config.settings import settings


class DatabaseService:
    """Supabase database service"""

    def __init__(self):
        """Initialize Supabase client"""
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key
        )

    def get_all_patients(self):
        """Get all patients from database (8 patients)"""
        response = self.client.table("patients").select("*").execute()
        return response.data

    def get_patient_by_id(self, patient_id: str):
        """Get a specific patient by ID"""
        response = self.client.table("patients").select("*").eq("id", patient_id).execute()
        return response.data[0] if response.data else None

    def get_available_doctors(self):
        """Get all available doctors"""
        response = self.client.table("doctors").select("*").eq("available", True).execute()
        return response.data

    def get_all_services(self):
        """Get all dental services"""
        response = self.client.table("services").select("*").execute()
        return response.data


# Singleton instance
_db_instance = None


def get_database() -> DatabaseService:
    """Get or create database service instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseService()
    return _db_instance
