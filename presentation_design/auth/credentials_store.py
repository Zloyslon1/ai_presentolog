"""
Credentials Storage Module
===========================

Secure storage and retrieval of OAuth 2.0 credentials.
Handles token persistence, encryption, and access control.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CredentialsStore:
    """
    Manages storage and retrieval of OAuth 2.0 credentials.
    
    Stores access tokens, refresh tokens, and expiration information
    in a secure location with appropriate file permissions.
    
    Attributes:
        token_path (Path): Path to token storage file
    """
    
    def __init__(self, token_path: str):
        """
        Initialize credentials store.
        
        Args:
            token_path: Path to token storage file
        """
        self.token_path = Path(token_path)
        self._ensure_secure_permissions()
    
    def _ensure_secure_permissions(self) -> None:
        """
        Ensure credential directory has secure permissions.
        
        Creates directory if it doesn't exist and sets appropriate permissions.
        On Unix systems, sets directory to 0700 (owner-only access).
        """
        # Create directory if it doesn't exist
        self.token_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set secure permissions on Unix systems
        if os.name != 'nt':  # Not Windows
            try:
                os.chmod(self.token_path.parent, 0o700)
                if self.token_path.exists():
                    os.chmod(self.token_path, 0o600)
            except Exception as e:
                logger.warning(f"Could not set secure permissions: {e}")
    
    def store_credentials(self, credentials: Dict[str, Any]) -> None:
        """
        Store OAuth credentials to file.
        
        Args:
            credentials: Dictionary containing credential data with keys:
                - access_token: Current access token
                - refresh_token: Refresh token for obtaining new access tokens
                - token_expiry: Expiration timestamp
                - token_uri: Token endpoint URI
                - client_id: OAuth client ID
                - client_secret: OAuth client secret
                - scopes: List of authorized scopes
                
        Raises:
            IOError: If unable to write credentials file
        """
        try:
            # Prepare credentials data for storage
            creds_data = {
                'access_token': credentials.get('access_token'),
                'refresh_token': credentials.get('refresh_token'),
                'token_expiry': credentials.get('token_expiry'),
                'token_uri': credentials.get('token_uri'),
                'client_id': credentials.get('client_id'),
                'client_secret': credentials.get('client_secret'),
                'scopes': credentials.get('scopes', []),
                'stored_at': datetime.utcnow().isoformat()
            }
            
            # Write to file
            with open(self.token_path, 'w', encoding='utf-8') as f:
                json.dump(creds_data, f, indent=2)
            
            # Set secure permissions on newly created file
            if os.name != 'nt':
                os.chmod(self.token_path, 0o600)
            
            logger.info(
                "Credentials stored successfully",
                operation="store_credentials",
                token_path=str(self.token_path)
            )
            
        except Exception as e:
            logger.error(
                f"Failed to store credentials: {e}",
                operation="store_credentials",
                exc_info=True
            )
            raise IOError(f"Failed to store credentials: {e}") from e
    
    def load_credentials(self) -> Optional[Dict[str, Any]]:
        """
        Load OAuth credentials from file.
        
        Returns:
            Dictionary containing credential data, or None if file doesn't exist
            
        Raises:
            IOError: If unable to read or parse credentials file
        """
        if not self.token_path.exists():
            logger.debug(
                "Credentials file does not exist",
                operation="load_credentials",
                token_path=str(self.token_path)
            )
            return None
        
        try:
            with open(self.token_path, 'r', encoding='utf-8') as f:
                creds_data = json.load(f)
            
            logger.info(
                "Credentials loaded successfully",
                operation="load_credentials",
                token_path=str(self.token_path)
            )
            
            return creds_data
            
        except json.JSONDecodeError as e:
            logger.error(
                f"Invalid JSON in credentials file: {e}",
                operation="load_credentials",
                exc_info=True
            )
            raise IOError(f"Invalid credentials file format: {e}") from e
        except Exception as e:
            logger.error(
                f"Failed to load credentials: {e}",
                operation="load_credentials",
                exc_info=True
            )
            raise IOError(f"Failed to load credentials: {e}") from e
    
    def is_token_valid(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if stored token is still valid.
        
        Args:
            credentials: Credentials to check. If None, loads from file.
            
        Returns:
            True if token exists and is not expired, False otherwise
        """
        if credentials is None:
            credentials = self.load_credentials()
        
        if credentials is None:
            return False
        
        # Check if access token exists
        if not credentials.get('access_token'):
            return False
        
        # Check expiration
        token_expiry = credentials.get('token_expiry')
        if not token_expiry:
            # No expiry info, assume valid (will be checked on API call)
            return True
        
        try:
            # Parse expiry timestamp
            if isinstance(token_expiry, str):
                expiry_time = datetime.fromisoformat(token_expiry.replace('Z', '+00:00'))
            else:
                expiry_time = token_expiry
            
            # Add buffer time (5 minutes) to avoid using token that's about to expire
            now = datetime.utcnow()
            buffer = timedelta(minutes=5)
            
            is_valid = now + buffer < expiry_time
            
            logger.debug(
                f"Token validity check: {'valid' if is_valid else 'expired'}",
                operation="is_token_valid",
                expiry=token_expiry
            )
            
            return is_valid
            
        except (ValueError, TypeError) as e:
            logger.warning(
                f"Could not parse token expiry: {e}",
                operation="is_token_valid"
            )
            # If we can't parse expiry, assume invalid
            return False
    
    def has_refresh_token(self, credentials: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if credentials contain a refresh token.
        
        Args:
            credentials: Credentials to check. If None, loads from file.
            
        Returns:
            True if refresh token exists, False otherwise
        """
        if credentials is None:
            credentials = self.load_credentials()
        
        if credentials is None:
            return False
        
        return bool(credentials.get('refresh_token'))
    
    def delete_credentials(self) -> None:
        """
        Delete stored credentials.
        
        Used for re-authentication or cleanup.
        """
        if self.token_path.exists():
            try:
                self.token_path.unlink()
                logger.info(
                    "Credentials deleted",
                    operation="delete_credentials",
                    token_path=str(self.token_path)
                )
            except Exception as e:
                logger.error(
                    f"Failed to delete credentials: {e}",
                    operation="delete_credentials",
                    exc_info=True
                )
                raise IOError(f"Failed to delete credentials: {e}") from e
    
    def credentials_exist(self) -> bool:
        """
        Check if credentials file exists.
        
        Returns:
            True if credentials file exists, False otherwise
        """
        return self.token_path.exists()
    
    def get_credential_info(self) -> Dict[str, Any]:
        """
        Get information about stored credentials without exposing sensitive data.
        
        Returns:
            Dictionary with non-sensitive credential information
        """
        if not self.credentials_exist():
            return {
                'exists': False,
                'valid': False,
                'has_refresh_token': False
            }
        
        credentials = self.load_credentials()
        
        return {
            'exists': True,
            'valid': self.is_token_valid(credentials),
            'has_refresh_token': self.has_refresh_token(credentials),
            'scopes': credentials.get('scopes', []) if credentials else [],
            'stored_at': credentials.get('stored_at') if credentials else None,
            'token_expiry': credentials.get('token_expiry') if credentials else None
        }
