"""
Text Parser Module
==================

Parses raw text input into structured slide data.
Adapted from index-7.html JavaScript parsing logic.
"""

import re
from typing import List, Dict, Optional


class TextParser:
    """Parse raw text into structured slide data."""
    
    def __init__(self):
        self.slides = []
    
    def parse_slides(self, text: str) -> List[Dict]:
        """Main parsing method.
        
        Args:
            text: Raw text input from user
            
        Returns:
            List of slide dictionaries
        """
        print('🔍 Starting text parsing...')
        
        # Try strategy 1: Number after text
        matches = self.detect_number_after_pattern(text)
        if matches:
            print(f'✅ Found {len(matches)} slides with number-after pattern')
            return self.parse_number_after_slides(text, matches)
        
        # Try strategy 2: Explicit markers
        matches = self.detect_slide_markers(text)
        if matches:
            print(f'✅ Found {len(matches)} slides with explicit markers')
            return self.parse_marked_slides(text, matches)
        
        # Fallback: Intelligent block analysis
        print('⚙️ Using intelligent block analysis...')
        return self.detect_intelligent_blocks(text)
    
    def detect_number_after_pattern(self, text: str) -> List[Dict]:
        """Detect slides by number on separate line.
        
        Pattern: Text content followed by number on new line
        Example:
            Content here
            1
            
            More content
            2
        """
        pattern = r'\n(\d+)\s*$'
        matches = []
        for match in re.finditer(pattern, text, re.MULTILINE):
            matches.append({
                'number': match.group(1),
                'index': match.start(),
                'end': match.end()
            })
        return matches
    
    def detect_slide_markers(self, text: str) -> List[Dict]:
        """Detect explicit slide markers.
        
        Pattern: "Slide N" or "Слайд N"
        Example: "Slide 1", "Слайд 2"
        """
        pattern = r'(?:^|\n)(slide|слайд)\s*(\d+)(?:\s+(.*))?'
        matches = []
        for match in re.finditer(pattern, text, re.IGNORECASE):
            matches.append({
                'number': match.group(2),
                'index': match.start(),
                'title_on_same_line': match.group(3).strip() if match.group(3) else None
            })
        return matches
    
    def parse_number_after_slides(self, text: str, matches: List[Dict]) -> List[Dict]:
        """Parse slides when numbers follow content."""
        slides = []
        previous_end = 0
        
        for i, match in enumerate(matches):
            content = text[previous_end:match['index']].strip()
            if content:
                slide = self.create_slide_from_content(content, match['number'])
                slides.append(slide)
            previous_end = match['end']
        
        # Handle remaining text
        remaining = text[previous_end:].strip()
        if remaining:
            slide = self.create_slide_from_content(
                remaining, 
                str(len(slides) + 1)
            )
            slides.append(slide)
        
        return slides
    
    def parse_marked_slides(self, text: str, matches: List[Dict]) -> List[Dict]:
        """Parse slides with explicit 'Slide N' markers."""
        slides = []
        
        for i, match in enumerate(matches):
            # Get content between this marker and next (or end of text)
            content_start = match['index'] + len('слайд ' + match['number'])
            content_end = matches[i + 1]['index'] if i + 1 < len(matches) else len(text)
            
            content = text[content_start:content_end].strip()
            
            # If title was on same line, prepend it
            if match['title_on_same_line']:
                content = match['title_on_same_line'] + '\n' + content
            
            slide = self.create_slide_from_content(content, match['number'])
            slides.append(slide)
        
        return slides
    
    def detect_intelligent_blocks(self, text: str) -> List[Dict]:
        """Analyze text blocks separated by empty lines.
        
        Classify as titles, content, or slide breaks.
        """
        blocks = text.split('\n\n')
        slides = []
        current_slide = None
        
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            
            lines = block.split('\n')
            first_line = lines[0].strip()
            word_count = self.count_words(first_line)
            
            # Detect if this starts a new slide
            # Check for slide markers or if we don't have a current slide
            if self.is_slide_start(first_line) or current_slide is None:
                if current_slide:
                    slides.append(current_slide)
                current_slide = {'title': '', 'content': []}
            
            # Classify block
            if not current_slide['title'] and word_count <= 6:
                current_slide['title'] = first_line
                if len(lines) > 1:
                    current_slide['content'].extend(lines[1:])
            else:
                current_slide['content'].extend(lines)
        
        # Add last slide
        if current_slide:
            slides.append(current_slide)
        
        # Convert to standard format
        result = []
        for i, slide in enumerate(slides):
            result.append({
                'id': str(i + 1),
                'title': slide['title'],
                'mainText': '\n'.join(slide['content']),
                'secondaryText': ''
            })
        
        return result if result else [{'id': '1', 'title': '', 'mainText': text, 'secondaryText': ''}]
    
    def is_slide_start(self, line: str) -> bool:
        """Check if line indicates start of new slide."""
        # Check for slide markers
        if re.match(r'^(slide|слайд)\s*\d+', line, re.IGNORECASE):
            return True
        # Check for numbered headers
        if re.match(r'^\d+\.', line):
            return True
        # Check for markdown headers
        if re.match(r'^#{1,3}\s', line):
            return True
        return False
    
    def create_slide_from_content(self, content: str, slide_id: str) -> Dict:
        """Create slide dictionary from text content.
        
        Extracts title from first line(s) if they look like a title.
        """
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        
        if not lines:
            return {
                'id': slide_id,
                'title': '',
                'mainText': '',
                'secondaryText': ''
            }
        
        # Extract title from first line(s)
        title = ''
        content_start_idx = 0
        
        # Check if first line looks like a title (short, no punctuation at end except question mark)
        first_line = lines[0]
        
        # Title heuristics:
        # - Less than 100 chars
        # - Doesn't end with common sentence endings (., :, ;)
        # - Doesn't start with bullet/number (unless it's a lesson/topic number)
        is_title_like = (
            len(first_line) <= 100 and
            not first_line.endswith(('.', ':', ';', ',')) and
            not first_line.startswith(('• ', '- ', '* ')) and
            not re.match(r'^\d+[\.\)]\s', first_line)  # Not a list item like "1. something"
        )
        
        if is_title_like:
            title = first_line
            content_start_idx = 1
            
            # Check if second line is also part of title (subtitle-like)
            if len(lines) > 1:
                second_line = lines[1]
                is_subtitle_like = (
                    len(second_line) <= 80 and
                    not second_line.endswith(('.', ':', ';', ',')) and
                    not second_line.startswith(('• ', '- ', '* ')) and
                    not re.match(r'^\d+[\.\)]\s', second_line)
                )
                
                # If second line is short and title-like, combine them
                if is_subtitle_like and len(second_line) < len(first_line):
                    title = first_line + '\n' + second_line
                    content_start_idx = 2
        
        # Remaining lines are main text
        remaining_lines = lines[content_start_idx:]
        main_text = self.format_content(remaining_lines) if remaining_lines else ''
        
        return {
            'id': slide_id,
            'title': title,
            'mainText': main_text,
            'secondaryText': ''
        }
    
    def format_content(self, lines: List[str]) -> str:
        """Format lines into HTML content."""
        formatted = self.format_list_items(lines)
        formatted = self.apply_emphasis(formatted)
        return formatted
    
    def count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.strip().split())
    
    def format_list_items(self, lines: List[str]) -> str:
        """Convert lines with colons and bullets to HTML lists."""
        html = []
        in_list = False
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                if in_list:
                    html.append('</ul>')
                    in_list = False
                html.append('')
                continue
            
            # Line ending with colon -> bold + start list
            if stripped.endswith(':'):
                if in_list:
                    html.append('</ul>')
                    in_list = False
                html.append(f'<strong>{stripped}</strong>')
                html.append('<ul>')
                in_list = True
                continue
            
            # List item (bullets or dashes)
            if stripped.startswith(('• ', '- ', '* ')):
                if not in_list:
                    html.append('<ul>')
                    in_list = True
                # Remove marker and add as list item
                html.append(f'<li>{stripped[2:].strip()}</li>')
                continue
            
            # Numbered list
            if re.match(r'^\d+[\.\)]\s', stripped):
                # For now, treat as bullet list
                # Could enhance to use <ol> later
                if not in_list:
                    html.append('<ul>')
                    in_list = True
                # Remove number and add as list item
                text = re.sub(r'^\d+[\.\)]\s*', '', stripped)
                html.append(f'<li>{text}</li>')
                continue
            
            # Regular line
            if in_list:
                html.append('</ul>')
                in_list = False
            html.append(f'<p>{stripped}</p>')
        
        if in_list:
            html.append('</ul>')
        
        return '\n'.join(html)
    
    def apply_emphasis(self, text: str) -> str:
        """Apply bold and italic formatting.
        
        Patterns:
        - **text** or __text__ -> <strong>text</strong>
        - *text* or _text_ -> <em>text</em>
        """
        # **text** -> <strong>text</strong>
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # __text__ -> <strong>text</strong>
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        # *text* -> <em>text</em> (only if not already part of **)
        text = re.sub(r'(?<!\*)\*([^\*]+?)\*(?!\*)', r'<em>\1</em>', text)
        # _text_ -> <em>text</em> (only if not already part of __)
        text = re.sub(r'(?<!_)_([^_]+?)_(?!_)', r'<em>\1</em>', text)
        return text
