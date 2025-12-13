import os
import pytest
from unittest.mock import patch
from database.local_postgres import get_local_postgres_session_service

class TestLocalPostgresSession:
    @patch("database.local_postgres.DatabaseSessionService")
    def test_initialization_defaults(self, mock_service_cls):
        """Verify service initializes with default env vars."""
        # Clear relevant env vars to ensure defaults are tested
        with patch.dict(os.environ, {}, clear=True):
            service = get_local_postgres_session_service()
            
            # Assert default connection string is constructed correctly
            # Default: user:password@localhost:5432/sessions
            expected_url = "postgresql+pg8000://user:password@localhost:5432/sessions"
            mock_service_cls.assert_called_once_with(db_url=expected_url)
            assert service == mock_service_cls.return_value

    @patch("database.local_postgres.DatabaseSessionService")
    def test_initialization_custom(self, mock_service_cls):
        """Verify service initializes with custom env vars."""
        custom_env = {
            "POSTGRES_USER": "custom_user",
            "POSTGRES_PASSWORD": "custom_pass",
            "POSTGRES_DB": "custom_db",
            "POSTGRES_HOST": "custom_host",
            "POSTGRES_PORT": "9999"
        }
        with patch.dict(os.environ, custom_env):
            get_local_postgres_session_service()
            
            expected_url = "postgresql+pg8000://custom_user:custom_pass@custom_host:9999/custom_db"
            mock_service_cls.assert_called_once_with(db_url=expected_url)
