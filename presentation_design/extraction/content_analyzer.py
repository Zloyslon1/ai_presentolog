"""
Content Analyzer Module
========================

Advanced content analysis to recognize structure: titles, subtitles,
numbered lists, bullet lists, and logical content groupings.
"""

import re
from typing import Dict, Any, List, Tuple
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ContentAnalyzer:
    """
    Analyzes text content to identify structure and formatting needs.
    
    Recognizes:
    - Titles and subtitles
    - Numbered lists (1., 2., 3. or 1), 2), 3))
    - Bullet lists (•, -, *, –)
    - Emphasis patterns (ALL CAPS, bold markers)
    - Logical sections within slides
    """
    
    # Patterns for list detection
    NUMBERED_LIST_PATTERN = re.compile(r'^\s*(\d+)[.):]\s+(.+)', re.MULTILINE)
    BULLET_PATTERN = re.compile(r'^\s*[•\-\*–—]\s+(.+)', re.MULTILINE)
    
    # Patterns for emphasis
    ALL_CAPS_PATTERN = re.compile(r'^[A-ZА-ЯЁ\s\d\W]+$')
    
    @staticmethod
    def analyze_text_structure(text: str) -> Dict[str, Any]:
        """
        Analyze text to determine its structure.
        
        Args:
            text: Raw text content
            
        Returns:
            Dictionary with structure information:
            {
                'content_type': 'plain' | 'numbered_list' | 'bullet_list' | 'mixed',
                'items': [list of text items],
                'has_emphasis': bool,
                'is_title_case': bool
            }
        """
        if not text or not text.strip():
            return {
                'content_type': 'plain',
                'items': [],
                'has_emphasis': False,
                'is_title_case': False
            }
        
        # Check for numbered list
        numbered_matches = list(ContentAnalyzer.NUMBERED_LIST_PATTERN.finditer(text))
        
        # Check for bullet list
        bullet_matches = list(ContentAnalyzer.BULLET_PATTERN.finditer(text))
        
        # Determine content type
        if numbered_matches and len(numbered_matches) >= 2:
            content_type = 'numbered_list'
            items = [match.group(2).strip() for match in numbered_matches]
        elif bullet_matches and len(bullet_matches) >= 2:
            content_type = 'bullet_list'
            items = [match.group(1).strip() for match in bullet_matches]
        else:
            content_type = 'plain'
            items = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Check for emphasis
        has_emphasis = bool(ContentAnalyzer.ALL_CAPS_PATTERN.match(text.strip()))
        
        # Check if title case (first letters capitalized)
        is_title_case = ContentAnalyzer._is_title_case(text)
        
        return {
            'content_type': content_type,
            'items': items,
            'has_emphasis': has_emphasis,
            'is_title_case': is_title_case,
            'original_text': text
        }
    
    @staticmethod
    def _is_title_case(text: str) -> bool:
        """Check if text appears to be in title case."""
        words = text.split()
        if not words:
            return False
        
        # At least 50% of words should start with capital
        capitalized = sum(1 for word in words if word and word[0].isupper())
        return capitalized / len(words) >= 0.5
    
    @staticmethod
    def detect_slide_sections(elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze all elements on a slide to group them into logical sections.
        
        Args:
            elements: List of parsed text elements
            
        Returns:
            List of elements with enhanced role detection and grouping
        """
        if not elements:
            return []
        
        enhanced_elements = []
        
        # Sort elements by Y position (top to bottom)
        sorted_elements = sorted(
            elements, 
            key=lambda e: e.get('position', {}).get('translateY', 0)
        )
        
        for idx, element in enumerate(sorted_elements):
            enhanced = element.copy()
            
            # Analyze text structure
            text_analysis = ContentAnalyzer.analyze_text_structure(element['content'])
            enhanced['text_analysis'] = text_analysis
            
            # Refine role based on content analysis
            refined_role = ContentAnalyzer._refine_role(
                element, 
                text_analysis, 
                idx, 
                len(sorted_elements)
            )
            enhanced['role'] = refined_role
            
            enhanced_elements.append(enhanced)
        
        logger.info(
            f"Analyzed slide structure: {len(enhanced_elements)} elements",
            operation="detect_slide_sections"
        )
        
        return enhanced_elements
    
    @staticmethod
    def _refine_role(
        element: Dict[str, Any], 
        text_analysis: Dict[str, Any],
        position_index: int,
        total_elements: int
    ) -> str:
        """
        Refine element role based on content analysis.
        
        Args:
            element: Original element data
            text_analysis: Structure analysis results
            position_index: Position in sorted elements (0 = top)
            total_elements: Total number of elements
            
        Returns:
            Refined role string
        """
        current_role = element.get('role', 'BODY')
        content = element.get('content', '').strip()
        
        # If already marked as TITLE or SUBTITLE, keep it unless contradicted
        if current_role in ['TITLE', 'SUBTITLE']:
            # But if it's a list, change to HEADING + list
            if text_analysis['content_type'] in ['numbered_list', 'bullet_list']:
                return 'HEADING'
            return current_role
        
        # First element that's short and emphasized = likely TITLE
        if position_index == 0:
            if len(content) < 100 and (
                text_analysis['has_emphasis'] or 
                text_analysis['is_title_case']
            ):
                return 'TITLE'
        
        # Second element on first slide = likely SUBTITLE
        if position_index == 1 and total_elements >= 2:
            if len(content) < 150:
                return 'SUBTITLE'
        
        # Short text with emphasis = HEADING
        if len(content) < 100 and text_analysis['has_emphasis']:
            return 'HEADING'
        
        # Lists remain as BODY but are marked in text_analysis
        if text_analysis['content_type'] in ['numbered_list', 'bullet_list']:
            return 'BODY'
        
        # Last element in a long list = likely FOOTER
        if position_index == total_elements - 1 and len(content) < 50:
            return 'FOOTER'
        
        return 'BODY'
    
    @staticmethod
    def format_list_items(items: List[str], list_type: str) -> str:
        """
        Format list items with proper markers.
        
        Args:
            items: List of text items
            list_type: 'numbered_list' or 'bullet_list'
            
        Returns:
            Formatted text with consistent list markers
        """
        if list_type == 'numbered_list':
            return '\n'.join(f"{i+1}. {item}" for i, item in enumerate(items))
        elif list_type == 'bullet_list':
            return '\n'.join(f"• {item}" for item in items)
        else:
            return '\n'.join(items)
