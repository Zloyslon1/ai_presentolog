"""
Web OAuth Manager for Flask
============================

Handles OAuth 2.0 authentication flow for web applications.
Each user authenticates with their own Google account.
Tokens stored in Flask session.
"""

import os
import json
from flask import session, url_for, request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from typing import Optional

# OAuth scopes
SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/presentations.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

# Disable OAuthlib's HTTPS verification for local development
# IMPORTANT: Remove this in production!
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


class WebOAuthManager:
    """
    Manages OAuth 2.0 authentication for Flask web app.
    
    Each user gets their own credentials stored in Flask session.
    """
    
    def __init__(self, client_secrets_file: str):
        """
        Initialize Web OAuth Manager.
        
        Args:
            client_secrets_file: Path to Google OAuth client secrets JSON
        """
        self.client_secrets_file = client_secrets_file
        self.scopes = SCOPES
    
    def get_authorization_url(self, redirect_uri: str) -> str:
        """
        Get authorization URL for OAuth flow.
        
        Args:
            redirect_uri: Where to redirect after authorization
            
        Returns:
            Authorization URL to redirect user to
        """
        flow = Flow.from_client_secrets_file(
            self.client_secrets_file,
            scopes=self.scopes,
            redirect_uri=redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent screen to get refresh token
        )
        
        # Store state in session for security
        session['oauth_state'] = state
        
        return authorization_url
    
    def handle_oauth_callback(self, redirect_uri: str, authorization_response: str):
        """
        Handle OAuth callback and store credentials in session.
        
        Args:
            redirect_uri: Redirect URI used in authorization
            authorization_response: Full authorization response URL
        """
        # Verify state to prevent CSRF
        state = session.get('oauth_state')
        
        flow = Flow.from_client_secrets_file(
            self.client_secrets_file,
            scopes=self.scopes,
            state=state,
            redirect_uri=redirect_uri
        )
        
        # Fetch token
        flow.fetch_token(authorization_response=authorization_response)
        
        # Store credentials in session
        credentials = flow.credentials
        session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
    
    def get_credentials(self) -> Optional[Credentials]:
        """
        Get credentials from session with automatic refresh.
        
        Returns:
            Credentials object or None if not authenticated
        """
        if 'credentials' not in session:
            return None
        
        creds_data = session['credentials']
        
        try:
            credentials = Credentials(
                token=creds_data.get('token'),
                refresh_token=creds_data.get('refresh_token'),
                token_uri=creds_data.get('token_uri'),
                client_id=creds_data.get('client_id'),
                client_secret=creds_data.get('client_secret'),
                scopes=creds_data.get('scopes')
            )
            
            # Refresh if expired
            if credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                    # Update session with refreshed credentials
                    session['credentials'] = {
                        'token': credentials.token,
                        'refresh_token': credentials.refresh_token,
                        'token_uri': credentials.token_uri,
                        'client_id': credentials.client_id,
                        'client_secret': credentials.client_secret,
                        'scopes': credentials.scopes
                    }
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    # Clear invalid credentials
                    self.logout()
                    return None
            
            return credentials
        except Exception as e:
            print(f"Error reconstructing credentials: {e}")
            return None
    
    def get_user_info(self) -> Optional[dict]:
        """
        Get user information from Google.
        
        Returns:
            Dictionary with user info (email, name, etc.) or None if failed
        """
        credentials = self.get_credentials()
        if not credentials:
            return None
        
        try:
            from googleapiclient.discovery import build
            oauth_service = build('oauth2', 'v2', credentials=credentials)
            user_info = oauth_service.userinfo().get().execute()
            return user_info
        except Exception as e:
            print(f"Error retrieving user info: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated.
        
        Returns:
            True if user has valid credentials
        """
        credentials = self.get_credentials()
        return credentials is not None and credentials.valid
    
    def logout(self):
        """Remove credentials from session (logout user)."""
        if 'credentials' in session:
            session.pop('credentials')
        if 'oauth_state' in session:
            session.pop('oauth_state')
