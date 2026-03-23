"""
Date Extractor Component
Uses NLP/AI to extract dates and events from email text
"""

import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import dateparser
import spacy

logger = logging.getLogger(__name__)


class DateExtractor:
    """Extracts dates and events from email text using NLP"""
    
    def __init__(self):
        """Initialize the date extractor with spaCy NLP model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy NLP model")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def extract_dates_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract dates and events from email text
        
        Args:
            text: Email text to extract dates from
            
        Returns:
            List of dictionaries containing extracted dates and event descriptions
        """
        if not text:
            return []
        
        events = []
        
        # Pattern matching for common date formats
        events.extend(self._extract_by_patterns(text))
        
        # NLP-based extraction if model is available
        if self.nlp:
            events.extend(self._extract_by_nlp(text))
        
        # Deduplicate and filter
        unique_events = self._deduplicate_events(events)
        
        logger.info(f"Extracted {len(unique_events)} events from text")
        return unique_events
    
    def _extract_by_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Extract dates using regex patterns"""
        events = []
        
        # Pattern: "on [date] at [time]"
        pattern1 = r"on\s+(\d{1,2}\s+\w+\s+\d{4}|\d{1,2}\s+\w+|\w+)\s+at\s+(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?)"
        matches = re.finditer(pattern1, text, re.IGNORECASE)
        for match in matches:
            date_str = match.group(1)
            time_str = match.group(2)
            parsed_date = dateparser.parse(f"{date_str} {time_str}")
            if parsed_date:
                events.append({
                    "date": parsed_date,
                    "description": f"Event at {time_str}",
                    "confidence": 0.9,
                    "source": "pattern_matching"
                })
        
        # Pattern: "meeting on [date]"
        pattern2 = r"(?:meeting|appointment|event|deadline)\s+(?:on|scheduled for)?\s+(\d{1,2}\s+\w+\s+\d{4}|\d{1,2}\s+\w+)"
        matches = re.finditer(pattern2, text, re.IGNORECASE)
        for match in matches:
            date_str = match.group(1)
            parsed_date = dateparser.parse(date_str)
            if parsed_date:
                events.append({
                    "date": parsed_date,
                    "description": match.group(0),
                    "confidence": 0.85,
                    "source": "pattern_matching"
                })
        
        # Pattern: "21 March 2024"
        pattern3 = r"\d{1,2}\s+\w+\s+\d{4}"
        matches = re.finditer(pattern3, text)
        for match in matches:
            date_str = match.group(0)
            parsed_date = dateparser.parse(date_str)
            if parsed_date:
                events.append({
                    "date": parsed_date,
                    "description": f"Date mentioned: {date_str}",
                    "confidence": 0.7,
                    "source": "pattern_matching"
                })
        
        return events
    
    def _extract_by_nlp(self, text: str) -> List[Dict[str, Any]]:
        """Extract dates using NLP entity recognition"""
        events = []
        
        try:
            doc = self.nlp(text)
            
            # Extract DATE and TIME entities
            for ent in doc.ents:
                if ent.label_ in ["DATE", "TIME"]:
                    parsed_date = dateparser.parse(ent.text)
                    if parsed_date:
                        events.append({
                            "date": parsed_date,
                            "description": ent.text,
                            "confidence": 0.8,
                            "source": "nlp"
                        })
        except Exception as e:
            logger.warning(f"NLP extraction failed: {e}")
        
        return events
    
    def _deduplicate_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate events (same date within 1 hour)"""
        if not events:
            return []
        
        unique_events = []
        for event in sorted(events, key=lambda x: x['confidence'], reverse=True):
            # Check if similar event already exists
            is_duplicate = False
            for existing in unique_events:
                time_diff = abs((event['date'] - existing['date']).total_seconds())
                if time_diff < 3600:  # Within 1 hour
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_events.append(event)
        
        return unique_events
    
    def extract_from_email(self, email: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract dates from an email dictionary
        
        Args:
            email: Email dictionary from EmailReader
            
        Returns:
            List of extracted events with email context
        """
        # Combine subject and body
        full_text = f"{email.get('subject', '')} {email.get('full_body', '')}"
        
        events = self.extract_dates_from_text(full_text)
        
        # Add email metadata to events
        for event in events:
            event['email_id'] = email.get('id')
            event['sender'] = email.get('sender')
            event['email_subject'] = email.get('subject')
        
        return events
    
    def is_upcoming_event(self, event_date: datetime, hours_ahead: int = 24) -> bool:
        """
        Check if event is upcoming (within specified hours)
        
        Args:
            event_date: Date of the event
            hours_ahead: Number of hours to look ahead
            
        Returns:
            True if event is upcoming, False otherwise
        """
        now = datetime.now(event_date.tzinfo) if event_date.tzinfo else datetime.now()
        time_until = (event_date - now).total_seconds() / 3600
        
        return 0 <= time_until <= hours_ahead
