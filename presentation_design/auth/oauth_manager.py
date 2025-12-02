"""
OAuth 2.0 Authentication Manager
=================================

Manages OAuth 2.0 authentication flow for Google APIs.
Handles token acquisition, refresh, and validation.
"""

import os
from typing import Optional, List
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from .credentials_store import CredentialsStore
from ..utils.logger import get_logger
from ..utils.retry import exponential_backoff

logger = get_logger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class OAuthManager:
    """
    Manages OAuth 2.0 authentication for Google APIs.
    
    Handles the complete OAuth flow including:
    - Initial user authorization
    - Token storage and retrieval
    - Automatic token refresh
    - Credential validation
    
    Attributes:
        scopes (List[str]): OAuth scopes requested
        client_secrets_path (Path): Path to client secrets file
        credentials_store (CredentialsStore): Credentials storage manager
        credentials (Optional[Credentials]): Current OAuth credentials
    """
    
    def __init__(
        self,
        client_secrets_path: str,
        token_path: str,
        scopes: List[str]
    ):
        """
        Initialize OAuth manager.
        
        Args:
            client_secrets_path: Path to Google OAuth client secrets JSON file
            token_path: Path to store OAuth tokens
            scopes: List of OAuth scopes to request
            
        Raises:
            AuthenticationError: If client secrets file not found
        """
        self.scopes = scopes
        self.client_secrets_path = Path(client_secrets_path)
        self.credentials_store = CredentialsStore(token_path)
        self.credentials: Optional[Credentials] = None
        
        # Validate client secrets exist
        if not self.client_secrets_path.exists():
            raise AuthenticationError(
                f"Client secrets file not found: {self.client_secrets_path}\n"
                "Please download OAuth credentials from Google Cloud Console."
            )
        
        logger.info(
            "OAuth manager initialized",
            operation="oauth_init",
            scopes=scopes
        )
    
    def authenticate(self, force_reauth: bool = False) -> Credentials:
        """
        Authenticate and return valid credentials.
        
        Attempts to load existing credentials, refresh if expired,
        or initiate new OAuth flow if needed.
        
        Args:
            force_reauth: If True, forces new authentication flow even if valid credentials exist
            
        Returns:
            Valid OAuth 2.0 Credentials object
            
        Raises:
            AuthenticationError: If authentication fails
        """
        # If forcing re-authentication, delete existing credentials
        if force_reauth:
            logger.info("Forcing re-authentication", operation="authenticate")
            self.credentials_store.delete_credentials()
            self.credentials = None
        
        # Try to load existing credentials
        if self.credentials is None and not force_reauth:
            self.credentials = self._load_credentials()
        
        # Refresh credentials if expired but refreshable
        if self.credentials and not self.credentials.valid:
            if self.credentials.expired and self.credentials.refresh_token:
                logger.info(
                    "Credentials expired, attempting refresh",
                    operation="authenticate"
                )
                self._refresh_credentials()
            else:
                # Credentials not refreshable, need new auth
                logger.warning(
                    "Credentials not refreshable, initiating new auth flow",
                    operation="authenticate"
                )
                self.credentials = None
        
        # If still no valid credentials, initiate OAuth flow
        if not self.credentials or not self.credentials.valid:
            logger.info(
                "No valid credentials, initiating OAuth flow",
                operation="authenticate"
            )
            self.credentials = self._run_oauth_flow()
        
        # Store credentials
        self._store_credentials()
        
        logger.info(
            "Authentication successful",
            operation="authenticate",
            scopes=self.scopes
        )
        
        return self.credentials
    
    def _load_credentials(self) -> Optional[Credentials]:
        """
        Load credentials from storage.
        
        Returns:
            Credentials object or None if not found or invalid
        """
        try:
            creds_data = self.credentials_store.load_credentials()
            
            if creds_data is None:
                return None
            
            # Create Credentials object from stored data
            credentials = Credentials(
                token=creds_data.get('access_token'),
                refresh_token=creds_data.get('refresh_token'),
                token_uri=creds_data.get('token_uri'),
                client_id=creds_data.get('client_id'),
                client_secret=creds_data.get('client_secret'),
                scopes=creds_data.get('scopes', self.scopes)
            )
            
            logger.info(
                "Credentials loaded from storage",
                operation="load_credentials"
            )
            
            return credentials
            
        except Exception as e:
            logger.error(
                f"Failed to load credentials: {e}",
                operation="load_credentials",
                exc_info=True
            )
            return None
    
    @exponential_backoff(max_retries=2, exceptions=(Exception,))
    def _refresh_credentials(self) -> None:
        """
        Refresh expired credentials.
        
        Raises:
            AuthenticationError: If refresh fails
        """
        try:
            if not self.credentials:
                raise AuthenticationError("No credentials to refresh")
            
            self.credentials.refresh(Request())
            
            logger.info(
                "Credentials refreshed successfully",
                operation="refresh_credentials"
            )
            
        except Exception as e:
            logger.error(
                f"Failed to refresh credentials: {e}",
                operation="refresh_credentials",
                exc_info=True
            )
            raise AuthenticationError(f"Failed to refresh credentials: {e}") from e
    
    def _run_oauth_flow(self) -> Credentials:
        """
        Run OAuth 2.0 authorization flow.
        
        Initiates browser-based authorization flow for user consent.
        
        Returns:
            New Credentials object
            
        Raises:
            AuthenticationError: If OAuth flow fails
        """
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.client_secrets_path),
                scopes=self.scopes
            )
            
            # Run local server flow
            logger.info(
                "Starting OAuth authorization flow",
                operation="oauth_flow"
            )
            
            credentials = flow.run_local_server(
                port=0,  # Use any available port
                prompt='consent',  # Force consent screen to ensure refresh token
                success_message='Authentication successful! You can close this window.'
            )
            
            logger.info(
                "OAuth flow completed successfully",
                operation="oauth_flow"
            )
            
            return credentials
            
        except Exception as e:
            logger.error(
                f"OAuth flow failed: {e}",
                operation="oauth_flow",
                exc_info=True
            )
            raise AuthenticationError(f"OAuth flow failed: {e}") from e
    
    def _store_credentials(self) -> None:
        """
        Store credentials to persistent storage.
        
        Raises:
            AuthenticationError: If storage fails
        """
        if not self.credentials:
            logger.warning(
                "No credentials to store",
                operation="store_credentials"
            )
            return
        
        try:
            creds_data = {
                'access_token': self.credentials.token,
                'refresh_token': self.credentials.refresh_token,
                'token_uri': self.credentials.token_uri,
                'client_id': self.credentials.client_id,
                'client_secret': self.credentials.client_secret,
                'scopes': self.credentials.scopes,
                'token_expiry': self.credentials.expiry.isoformat() if self.credentials.expiry else None
            }
            
            self.credentials_store.store_credentials(creds_data)
            
        except Exception as e:
            logger.error(
                f"Failed to store credentials: {e}",
                operation="store_credentials",
                exc_info=True
            )
            raise AuthenticationError(f"Failed to store credentials: {e}") from e
    
    def get_credentials(self, refresh_if_needed: bool = True) -> Credentials:
        """
        Get current credentials, refreshing if necessary.
        
        Args:
            refresh_if_needed: If True, refresh credentials if expired
            
        Returns:
            Valid Credentials object
            
        Raises:
            AuthenticationError: If credentials not available
        """
        if self.credentials is None:
            self.authenticate()
        
        if refresh_if_needed and self.credentials:
            if not self.credentials.valid and self.credentials.expired and self.credentials.refresh_token:
                self._refresh_credentials()
                self._store_credentials()
        
        if not self.credentials:
            raise AuthenticationError("No valid credentials available")
        
        return self.credentials
    
    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated with valid credentials.
        
        Returns:
            True if authenticated with valid credentials
        """
        if self.credentials is None:
            # Try to load from storage
            self.credentials = self._load_credentials()
        
        return self.credentials is not None and self.credentials.valid
    
    def revoke_credentials(self) -> None:
        """
        Revoke current credentials and delete from storage.
        
        Forces re-authentication on next use.
        """
        if self.credentials:
            try:
                # Revoke token with Google
                if self.credentials.token:
                    import requests
                    requests.post(
                        'https://oauth2.googleapis.com/revoke',
                        params={'token': self.credentials.token},
                        headers={'content-type': 'application/x-www-form-urlencoded'}
                    )
                
                logger.info(
                    "Credentials revoked",
                    operation="revoke_credentials"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to revoke token remotely: {e}",
                    operation="revoke_credentials"
                )
        
        # Delete local credentials
        self.credentials_store.delete_credentials()
        self.credentials = None
    
    def build_service(self, service_name: str, version: str):
        """
        Build Google API service client.
        
        Args:
            service_name: Name of Google service (e.g., 'slides', 'drive')
            version: API version (e.g., 'v1')
            
        Returns:
            Google API service client
            
        Raises:
            AuthenticationError: If authentication fails
        """
        credentials = self.get_credentials()
        
        try:
            service = build(service_name, version, credentials=credentials)
            
            logger.info(
                f"Built service client for {service_name} {version}",
                operation="build_service",
                service_name=service_name,
                version=version
            )
            
            return service
            
        except Exception as e:
            logger.error(
                f"Failed to build service client: {e}",
                operation="build_service",
                exc_info=True
            )
            raise AuthenticationError(f"Failed to build service client: {e}") from e
