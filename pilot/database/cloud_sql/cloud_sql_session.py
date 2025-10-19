
import os
from google.adk.sessions import DatabaseSessionService
from google.cloud.sql.connector import Connector

def get_cloud_sql_session_service():
    """Initializes and returns a DatabaseSessionService for Cloud SQL."""

    # 1. Get database credentials from environment variables
    db_user = os.environ.get("DB_USER")
    db_pass = os.environ.get("DB_PASS")
    db_name = os.environ.get("DB_NAME")
    instance_connection_name = os.environ.get("INSTANCE_CONNECTION_NAME")

    if not all([db_user, db_pass, db_name, instance_connection_name]):
        raise ValueError(
            "Missing one or more required database environment variables: "
            "DB_USER, DB_PASS, DB_NAME, INSTANCE_CONNECTION_NAME"
        )

    # 2. Initialize the Cloud SQL Connector
    connector = Connector()

    # 3. Define a function to get the database connection
    def getconn():
        conn = connector.connect(
            instance_connection_name,
            "pg8000",
            user=db_user,
            password=db_pass,
            db=db_name,
            ip_type=os.environ.get("DB_IP_TYPE", "public")
        )
        return conn

    # 4. Initialize the DatabaseSessionService
    session_service = DatabaseSessionService(
        db_url="postgresql+pg8000://",
        creator=getconn
    )
    return session_service
