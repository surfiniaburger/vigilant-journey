
import os
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler
from google.cloud import secretmanager
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from google.adk.sessions.base_session_service import BaseSessionService as SessionService
from google.adk.sessions.session import Session
from uuid import uuid4
from datetime import datetime

def setup_logging():
    """
    Set up Google Cloud Logging
    
    Returns:
        logging.Logger: Configured logger instance
    """
    gcp_logging_client = google.cloud.logging.Client()
    handler = CloudLoggingHandler(gcp_logging_client)
    logger = logging.getLogger('mongodb_connection')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger, handler, gcp_logging_client

def get_secret(project_id, secret_id, version_id="latest", logger=None):
    """
    Retrieve secret from Google Cloud Secret Manager.
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        if logger:
            logger.info(f"Attempting to access secret: {secret_id}")
        response = client.access_secret_version(request={"name": name})
        if logger:
            logger.info(f"Successfully retrieved secret: {secret_id}")
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        if logger:
            logger.error(f"Failed to retrieve secret {secret_id}: {str(e)}")
        raise

class MongoSessionService(SessionService):
    def __init__(self, client):
        self.client = client
        self.db = self.client.get_database("adk_sessions")
        self.sessions = self.db.get_collection("sessions")

    async def create_session(self, app_name: str, user_id: str, **kwargs) -> Session:
        session_id = str(uuid4())
        session_data = {
            "session_id": session_id,
            "app_name": app_name,
            "user_id": user_id,
            "created_at": datetime.utcnow(),
        }
        await self.sessions.insert_one(session_data)
        return Session(
            id=session_id, app_name=app_name, user_id=user_id, **kwargs
        )

    async def get_session(self, session_id: str) -> Session | None:
        session_data = await self.sessions.find_one({"session_id": session_id})
        if session_data:
            return Session(
                id=session_data["session_id"],
                app_name=session_data["app_name"],
                user_id=session_data["user_id"],
            )
        return None

    async def update_session(self, session: Session):
        # This is a no-op because the Session object from the ADK no longer has a metadata field or allows for arbitrary extra fields.
        pass

    async def delete_session(self, session_id: str):
        await self.sessions.delete_one({"session_id": session_id})
    
    async def list_sessions(self, app_name: str) -> list[Session]:
        """List all sessions for a given app name."""
        sessions_cursor = self.sessions.find({"app_name": app_name})
        sessions_list = await sessions_cursor.to_list(length=None)
        return [
            Session(
                id=session_data["session_id"],
                app_name=session_data["app_name"],
                user_id=session_data["user_id"],
            ) for session_data in sessions_list
        ]

def connect_to_mongodb():
    """
    Connect to MongoDB using URI from Secret Manager
    """
    logger, cloud_handler, gcp_log_client = setup_logging()
    try:
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "silver-455021")
        secret_id = "mongodb-uri"
        logger.info("Starting MongoDB connection process")
        uri = get_secret(project_id, secret_id, logger=logger)
        logger.info("Retrieved MongoDB URI from Secret Manager")
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        print("Successfully connected to MongoDB!")
        return client, logger, cloud_handler, gcp_log_client
    except Exception as e:
        error_message = f"Error connecting to MongoDB: {str(e)}"
        logger.error(error_message, exc_info=True)
        raise

def get_mongo_session_service():
    """Initializes and returns a MongoSessionService."""
    mongo_client, _, _, _ = connect_to_mongodb()
    return MongoSessionService(client=mongo_client)

if __name__ == "__main__":
    try:
        mongo_client, main_logger, main_cloud_handler, main_gcp_logging_client = connect_to_mongodb()
        if main_logger:
            main_logger.info("MongoDB connection process completed in __main__.")
    except Exception as e:
        print(f"Failed to connect: {e}")
    finally:
        # Clean up logging resources
        if 'main_cloud_handler' in locals() and main_cloud_handler:
            main_cloud_handler.close()
        if 'main_gcp_logging_client' in locals() and main_gcp_logging_client:
            main_gcp_logging_client.close()
        print("Script finished.")
