import os
import logging
from google.adk.sessions import DatabaseSessionService

logger = logging.getLogger(__name__)

def get_local_postgres_session_service():
    """
    Initializes and returns a DatabaseSessionService for local or standard PostgreSQL.
    
    This factory reads standard Postgres environment variables and constructs
    a connection string compatible with the ADK's DatabaseSessionService.
    It defaults to the values defined in docker-compose.yml for local development.
    """
    
    # 1. Get database credentials from environment variables (with local defaults)
    db_user = os.environ.get("POSTGRES_USER", "user")
    db_pass = os.environ.get("POSTGRES_PASSWORD", "password")
    db_name = os.environ.get("POSTGRES_DB", "sessions")
    db_host = os.environ.get("POSTGRES_HOST", "localhost")
    db_port = os.environ.get("POSTGRES_PORT", "5432")

    # 2. Construct the SQLAlchemy connection URL
    # We use pg8000 as the driver, consistent with the Cloud SQL implementation.
    # Format: postgresql+pg8000://user:password@host:port/database
    db_url = f"postgresql+pg8000://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    logger.info(f"Initializing Local Postgres Session Service for host: {db_host}")

    # 3. Initialize the DatabaseSessionService
    # Unlike Cloud SQL which needs a 'creator' function for the proprietary connector,
    # standard Postgres just needs the connection URL.
    session_service = DatabaseSessionService(
        db_url=db_url
    )
    return session_service
