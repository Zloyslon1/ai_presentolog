"""
Google Slides Content Extractor
================================

Extracts presentation content from Google Slides using the Slides API.
"""

import re
from typing import Dict, Any, Optional
from ..auth.oauth_manager import OAuthManager
from .content_parser import ContentParser
from ..utils.logger import get_logger
from ..utils.retry import retry_on_network_error

logger = get_logger(__name__)


class ExtractionError(Exception):
    """Raised when content extraction fails."""
    pass


class SlidesExtractor:
    """
    Extracts content from Google Slides presentations.
    
    Uses Google Slides API to retrieve presentation data and
    parses it into structured format for design application.
    
    Attributes:
        oauth_manager (OAuthManager): Authentication manager
        slides_service: Google Slides API service client
    """
    
    def __init__(self, oauth_manager: OAuthManager):
        """
        Initialize slides extractor.
        
        Args:
            oauth_manager: Configured OAuth manager
        """
        self.oauth_manager = oauth_manager
        self.slides_service = None
    
    def _ensure_service(self) -> None:
        """Ensure Slides API service is initialized."""
        if self.slides_service is None:
            self.slides_service = self.oauth_manager.build_service('slides', 'v1')
    
    @staticmethod
    def extract_presentation_id(url: str) -> str:
        """
        Extract presentation ID from Google Slides URL.
        
        Args:
            url: Google Slides URL or presentation ID
            
        Returns:
            Presentation ID
            
        Raises:
            ExtractionError: If URL format is invalid
        """
        # If already just an ID, return it
        if '/' not in url and len(url) > 20:
            return url
        
        # Extract from URL patterns:
        # https://docs.google.com/presentation/d/{ID}/edit
        # https://docs.google.com/presentation/d/{ID}
        pattern = r'/presentation/d/([a-zA-Z0-9-_]+)'
        match = re.search(pattern, url)
        
        if match:
            return match.group(1)
        
        raise ExtractionError(f"Invalid Google Slides URL format: {url}")
    
    @retry_on_network_error()
    def extract_presentation(self, presentation_url: str) -> Dict[str, Any]:
        """
        Extract complete presentation content.
        
        Args:
            presentation_url: Google Slides URL or presentation ID
            
        Returns:
            Parsed presentation data with structure and content
            
        Raises:
            ExtractionError: If extraction fails
        """
        try:
            # Extract presentation ID
            presentation_id = self.extract_presentation_id(presentation_url)
            
            logger.info(
                f"Extracting presentation {presentation_id}",
                operation="extract_presentation",
                presentation_id=presentation_id
            )
            
            # Ensure service is initialized
            self._ensure_service()
            
            # Fetch presentation data from API
            presentation_data = self.slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            logger.info(
                f"Retrieved presentation '{presentation_data.get('title')}'",
                operation="extract_presentation",
                presentation_id=presentation_id,
                slide_count=len(presentation_data.get('slides', []))
            )
            
            # Parse presentation structure
            parsed_data = ContentParser.parse_presentation(presentation_data)
            
            return parsed_data
            
        except ExtractionError:
            raise
        except Exception as e:
            logger.error(
                f"Failed to extract presentation: {e}",
                operation="extract_presentation",
                exc_info=True
            )
            raise ExtractionError(f"Failed to extract presentation: {e}") from e
    
    def extract_slide(self, presentation_id: str, slide_id: str) -> Dict[str, Any]:
        """
        Extract single slide content.
        
        Args:
            presentation_id: Google Slides presentation ID
            slide_id: Specific slide object ID
            
        Returns:
            Parsed slide data
        """
        try:
            self._ensure_service()
            
            # Fetch presentation to get specific slide
            presentation_data = self.slides_service.presentations().get(
                presentationId=presentation_id
            ).execute()
            
            # Find the specific slide
            for idx, slide in enumerate(presentation_data.get('slides', [])):
                if slide.get('objectId') == slide_id:
                    return ContentParser.parse_slide(slide, idx)
            
            raise ExtractionError(f"Slide {slide_id} not found in presentation")
            
        except Exception as e:
            logger.error(
                f"Failed to extract slide: {e}",
                operation="extract_slide",
                exc_info=True
            )
            raise ExtractionError(f"Failed to extract slide: {e}") from e
