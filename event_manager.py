"""
Event Manager Component
Stores and manages detected events in SQLite database
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Float, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)
Base = declarative_base()


class Event(Base):
    """SQLAlchemy model for calendar events"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True)
    event_date = Column(DateTime, nullable=False, index=True)
    description = Column(String, nullable=False)
    sender = Column(String)
    email_subject = Column(String)
    email_id = Column(String, unique=True)
    confidence = Column(Float, default=0.5)
    is_notified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "id": self.id,
            "event_date": self.event_date.isoformat(),
            "description": self.description,
            "sender": self.sender,
            "email_subject": self.email_subject,
            "email_id": self.email_id,
            "confidence": self.confidence,
            "is_notified": self.is_notified,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class EventManager:
    """Manages event storage and retrieval"""
    
    def __init__(self, database_url: str = "sqlite:///./email_calendar.db"):
        """
        Initialize event manager with database
        
        Args:
            database_url: Database connection URL
        """
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"Initialized EventManager with database: {database_url}")
    
    def add_event(self, event_data: Dict[str, Any]) -> Optional[Event]:
        """
        Add a new event to the database
        
        Args:
            event_data: Dictionary with event information
            
        Returns:
            Created Event object or None if failed
        """
        session = self.Session()
        try:
            # Check if email event already exists
            if event_data.get('email_id'):
                existing = session.query(Event).filter_by(
                    email_id=event_data.get('email_id')
                ).first()
                if existing:
                    logger.info(f"Event already exists for email {event_data.get('email_id')}")
                    return existing
            
            event = Event(
                event_date=event_data.get('date'),
                description=event_data.get('description', ''),
                sender=event_data.get('sender'),
                email_subject=event_data.get('email_subject'),
                email_id=event_data.get('email_id'),
                confidence=event_data.get('confidence', 0.5)
            )
            
            session.add(event)
            session.commit()
            logger.info(f"Added event: {event.description}")
            return event
        except Exception as e:
            logger.error(f"Error adding event: {e}")
            session.rollback()
            return None
        finally:
            session.close()
    
    def add_events_batch(self, events: List[Dict[str, Any]]) -> int:
        """
        Add multiple events to the database
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Number of events successfully added
        """
        count = 0
        for event_data in events:
            if self.add_event(event_data):
                count += 1
        return count
    
    def get_upcoming_events(self, hours_ahead: int = 24) -> List[Dict[str, Any]]:
        """
        Get upcoming events within specified hours
        
        Args:
            hours_ahead: Number of hours to look ahead
            
        Returns:
            List of upcoming events
        """
        session = self.Session()
        try:
            now = datetime.utcnow()
            from datetime import timedelta
            future = now + timedelta(hours=hours_ahead)
            
            events = session.query(Event).filter(
                Event.event_date >= now,
                Event.event_date <= future,
                Event.is_notified == False
            ).order_by(Event.event_date).all()
            
            return [event.to_dict() for event in events]
        except Exception as e:
            logger.error(f"Error getting upcoming events: {e}")
            return []
        finally:
            session.close()
    
    def get_all_events(self) -> List[Dict[str, Any]]:
        """Get all events from database"""
        session = self.Session()
        try:
            events = session.query(Event).order_by(Event.event_date).all()
            return [event.to_dict() for event in events]
        except Exception as e:
            logger.error(f"Error getting all events: {e}")
            return []
        finally:
            session.close()
    
    def mark_event_notified(self, event_id: int) -> bool:
        """Mark an event as notified"""
        session = self.Session()
        try:
            event = session.query(Event).filter_by(id=event_id).first()
            if event:
                event.is_notified = True
                session.commit()
                logger.info(f"Marked event {event_id} as notified")
                return True
            return False
        except Exception as e:
            logger.error(f"Error marking event as notified: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def delete_event(self, event_id: int) -> bool:
        """Delete an event"""
        session = self.Session()
        try:
            event = session.query(Event).filter_by(id=event_id).first()
            if event:
                session.delete(event)
                session.commit()
                logger.info(f"Deleted event {event_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_events_by_sender(self, sender: str) -> List[Dict[str, Any]]:
        """Get all events from a specific sender"""
        session = self.Session()
        try:
            events = session.query(Event).filter_by(sender=sender).order_by(Event.event_date).all()
            return [event.to_dict() for event in events]
        except Exception as e:
            logger.error(f"Error getting events by sender: {e}")
            return []
        finally:
            session.close()
