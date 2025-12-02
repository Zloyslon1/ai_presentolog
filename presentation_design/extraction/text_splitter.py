"""
Text Splitter Module
=====================

Intelligently splits raw text content into logical components:
title, subtitle, headings, body paragraphs, lists.
"""

import re
from typing import Dict, Any, List, Tuple
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TextSplitter:
    """
    Splits raw text into structured components.
    
    Instead of relying on Google Slides' structure, this analyzes
    the raw text content and intelligently divides it into:
    - Title (first line if short and prominent)
    - Subtitle (second line if exists)
    - Headings (short lines with emphasis)
    - Lists (numbered or bulleted)
    - Body paragraphs
    """
    
    @staticmethod
    def split_slide_text(text: str, slide_index: int) -> List[Dict[str, Any]]:
        """
        Split raw text into logical components.
        
        RULES (inspired by working HTML version):
        1. Title: ≤6 words = TITLE, ≥7 words = goes to MAIN TEXT
        2. Lines ending with ':' → **BOLD** + list follows
        3. List continues until empty line
        4. After empty line → SECONDARY TEXT
        
        Args:
            text: Raw text content from slide
            slide_index: Position of slide (0 = first slide)
            
        Returns:
            List of text components with roles and content
        """
        if not text or not text.strip():
            return []
        
        # Split into lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return []
        
        components = []
        i = 0
        
        # First slide OR regular slide with short first line
        if len(lines) > 0:
            first_line = lines[0]
            word_count = TextSplitter._count_words(first_line)
            
            # RULE 1: Title detection by word count
            if word_count <= 6:
                # Short line → TITLE
                components.append({
                    'role': 'TITLE',
                    'content': first_line,
                    'line_index': 0
                })
                i = 1
                
                # Second line on first slide = SUBTITLE
                if slide_index == 0 and len(lines) > 1 and len(lines[1]) < 150:
                    word_count_2 = TextSplitter._count_words(lines[1])
                    if word_count_2 <= 6:
                        components.append({
                            'role': 'SUBTITLE',
                            'content': lines[1],
                            'line_index': 1
                        })
                        i = 2
            # If first line is long (≥7 words), no title - goes directly to content
        
        # Process remaining lines with smart formatting
        if i < len(lines):
            remaining_lines = lines[i:]
            formatted_components = TextSplitter._format_text_with_lists(remaining_lines)
            components.extend(formatted_components)
        
        logger.info(
            f"Split text into {len(components)} components",
            operation="split_slide_text",
            slide_index=slide_index
        )
        
        return components
    
    @staticmethod
    def _count_words(text: str) -> int:
        """Count words in text (ignoring extra spaces)."""
        return len(text.strip().split())
    
    @staticmethod
    def _format_text_with_lists(lines: List[str]) -> List[Dict[str, Any]]:
        """
        Format lines with bold headers and lists.
        
        RULES:
        - Line ending with ':' → HEADING (will be made bold)
        - Lines after ':' → bullet list until empty line
        - After empty line → new section
        """
        components = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if line ends with colon → HEADING + list follows
            if line.endswith(':'):
                # Add heading
                components.append({
                    'role': 'HEADING',
                    'content': line,
                    'line_index': i,
                    'make_bold': True
                })
                i += 1
                
                # Collect list items that follow
                list_items = []
                while i < len(lines) and lines[i]:
                    # Stop if we hit another heading
                    if lines[i].endswith(':'):
                        break
                    # Stop if line is already a list item
                    if TextSplitter._is_list_item(lines[i]):
                        break
                    
                    list_items.append(lines[i])
                    i += 1
                
                # Add list as BODY with bullet markers
                if list_items:
                    list_content = '\n'.join(f"• {item}" for item in list_items)
                    components.append({
                        'role': 'BODY',
                        'content': list_content,
                        'content_type': 'bullet_list',
                        'is_list': True,
                        'items': list_items,
                        'line_index': i - len(list_items)
                    })
                
                continue
            
            # Check for numbered/bulleted list
            list_result, consumed = TextSplitter._extract_list(lines, i)
            if list_result:
                components.append(list_result)
                i += consumed
                continue
            
            # Check if it's a heading (short, ALL CAPS, or Title Case)
            if TextSplitter._is_heading(line):
                components.append({
                    'role': 'HEADING',
                    'content': line,
                    'line_index': i
                })
                i += 1
                continue
            
            # Regular paragraph - collect consecutive lines
            paragraph_lines = [line]
            i += 1
            
            while i < len(lines):
                next_line = lines[i]
                
                # Stop at headings or lists
                if (next_line.endswith(':') or 
                    TextSplitter._is_heading(next_line) or 
                    TextSplitter._is_list_item(next_line)):
                    break
                
                paragraph_lines.append(next_line)
                i += 1
            
            components.append({
                'role': 'BODY',
                'content': '\n'.join(paragraph_lines),
                'line_index': i - len(paragraph_lines)
            })
        
        return components
    
    @staticmethod
    def _is_heading(line: str) -> bool:
        """Check if line is a heading."""
        # Short line (< 80 chars)
        if len(line) > 80:
            return False
        
        # ALL CAPS
        if line.isupper() and len(line) > 3:
            return True
        
        # Ends with colon
        if line.endswith(':'):
            return True
        
        # Mostly capitalized words
        words = line.split()
        if len(words) > 0:
            capitalized = sum(1 for w in words if w and w[0].isupper())
            if capitalized / len(words) >= 0.7 and len(line) < 60:
                return True
        
        return False
    
    @staticmethod
    def _is_list_item(line: str) -> bool:
        """Check if line is a list item."""
        # Numbered: 1. 2) 3:
        if re.match(r'^\s*(\d+)[.):]\s+', line):
            return True
        
        # Bulleted: • - * – —
        if re.match(r'^\s*[•\-\*–—]\s+', line):
            return True
        
        return False
    
    @staticmethod
    def _extract_list(lines: List[str], start_idx: int) -> Tuple[Dict[str, Any], int]:
        """
        Extract a list starting from start_idx.
        
        Returns:
            (list_component, number_of_lines_consumed)
            or (None, 0) if not a list
        """
        if not TextSplitter._is_list_item(lines[start_idx]):
            return None, 0
        
        # Determine list type
        first_line = lines[start_idx]
        if re.match(r'^\s*(\d+)[.):]\s+', first_line):
            list_type = 'numbered_list'
        else:
            list_type = 'bullet_list'
        
        # Collect list items
        items = []
        i = start_idx
        
        while i < len(lines) and TextSplitter._is_list_item(lines[i]):
            # Extract item text (remove marker)
            line = lines[i]
            
            if list_type == 'numbered_list':
                match = re.match(r'^\s*\d+[.):]\s+(.+)', line)
                if match:
                    items.append(match.group(1))
            else:
                match = re.match(r'^\s*[•\-\*–—]\s+(.+)', line)
                if match:
                    items.append(match.group(1))
            
            i += 1
        
        # Format list content
        if list_type == 'numbered_list':
            content = '\n'.join(f"{idx+1}. {item}" for idx, item in enumerate(items))
        else:
            content = '\n'.join(f"• {item}" for item in items)
        
        return {
            'role': 'BODY',
            'content': content,
            'content_type': list_type,
            'is_list': True,
            'items': items,
            'line_index': start_idx
        }, i - start_idx
    
    @staticmethod
    def merge_slide_components(components: List[Dict[str, Any]]) -> str:
        """
        Merge components back into formatted text.
        Used for debugging.
        """
        result = []
        for comp in components:
            role = comp['role']
            content = comp['content']
            result.append(f"[{role}] {content}")
        return '\n\n'.join(result)
