from functools import lru_cache
from dateparser import parse
import re

class NLPProcessor:
    """Parse natural language task inputs"""
    @lru_cache(maxsize=128)
    def parse_command(self, text):
        """Extract task details from natural language"""
        # Try to extract date/time
        date = parse(text, settings={'PREFER_DATES_FROM': 'future'})
        due_date = date.date().isoformat() if date else None
        
        # Remove date phrases from description
        description = self.remove_date_phrases(text)
        
        # Auto-detect priority
        priority = self.detect_priority(text)
        
        return {
            "description": description,
            "due_date": due_date,
            "priority": priority
        }
    
    def remove_date_phrases(self, text):
        """Remove date/time phrases from text"""
        patterns = [
            r'\b(?:today|tomorrow|tonight)\b',
            r'\b\d{1,2}[:]\d{2}\s?(?:am|pm)?\b',
            r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b',
            r'\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(?:next week|next month|in \d+ days?)\b'
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
        return text.strip()
    
    def detect_priority(self, text):
        """Detect priority from text"""
        text = text.lower()
        if 'urgent' in text or 'important' in text or 'asap' in text:
            return 'high'
        if 'low priority' in text or 'when you can' in text:
            return 'low'
        return 'medium'