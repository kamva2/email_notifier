# Main application orchestrator
# Coordinates all components: Email Reader, Date Extractor, Event Manager, and Notification System


import logging
import schedule
import time
from typing import List, Dict, Any
from email_reader import EmailReader
from date_extractor import DateExtractor
from event_manager import EventManager
from notification_system import NotificationSystem
from config import Config, setup_logging

logger = logging.getLogger(__name__)


class EmailCalendarNotifier:
   
    
    def __init__(self, device_tokens: List[str] = None):
        
        # Initialize the email calendar notification system
        
        setup_logging()
        Config.validate()
        
        self.device_tokens = device_tokens or []
        
        # Initialize components
        self.email_reader = EmailReader(
            tenant_id=Config.TENANT_ID,
            client_id=Config.CLIENT_ID,
            client_secret=Config.CLIENT_SECRET
        )
        
        self.date_extractor = DateExtractor()
        self.event_manager = EventManager(database_url=Config.DATABASE_URL)
        
        self.notification_system = NotificationSystem(
            credentials_path=Config.FIREBASE_CREDENTIALS_PATH
        )
        
        logger.info("EmailCalendarNotifier initialized successfully")
    
    def process_emails(self) -> int:
        
        # Main workflow: fetch emails -> extract dates -> store events
        # Returns: Number of new events added

        try:
            logger.info("Starting email processing...")
            
            # Step 1: Fetch recent emails
            emails = self.email_reader.get_recent_emails(limit=50)
            logger.info(f"Fetched {len(emails)} emails")
            
            if not emails:
                logger.info("No emails to process")
                return 0
            
            # Step 2: Extract dates from each email
            all_events = []
            for email in emails:
                events = self.date_extractor.extract_from_email(email)
                all_events.extend(events)
                
                # Mark email as read after processing
                self.email_reader.mark_email_as_read(email['id'])
                logger.info(f"Processed email from {email.get('sender')}: found {len(events)} events")
            
            logger.info(f"Extracted {len(all_events)} total events from emails")
            
            # Step 3: Store events in database
            added_count = self.event_manager.add_events_batch(all_events)
            logger.info(f"Added {added_count} new events to database")
            
            return added_count
        
        except Exception as e:
            logger.error(f"Error in process_emails: {e}", exc_info=True)
            return 0
    
    def check_and_notify(self) -> int:
    
        # Check for upcoming events and send notifications

        try:
            logger.info("Checking for upcoming events...")
            
            # Get upcoming events that haven't been notified
            upcoming_events = self.event_manager.get_upcoming_events(
                hours_ahead=Config.NOTIFICATION_ADVANCE_HOURS
            )
            
            if not upcoming_events:
                logger.info("No upcoming events to notify")
                return 0
            
            logger.info(f"Found {len(upcoming_events)} upcoming events")
            
            notification_count = 0
            
            # Send notifications for each upcoming event
            for event in upcoming_events:
                if not self.device_tokens:
                    logger.warning("No device tokens configured for notifications")
                    break
                
                # Send to all registered devices
                for token in self.device_tokens:
                    success = self.notification_system.send_event_notification(token, event)
                    if success:
                        notification_count += 1
                        # Mark event as notified
                        self.event_manager.mark_event_notified(event['id'])
                        logger.info(f"Notification sent for event {event['id']}")
                    else:
                        logger.warning(f"Failed to send notification for event {event['id']}")
            
            logger.info(f"Sent {notification_count} notifications")
            return notification_count
        
        except Exception as e:
            logger.error(f"Error in check_and_notify: {e}", exc_info=True)
            return 0
    
    def run_scheduled(self):
        
        # Run the application with scheduled tasks
        # Emails are fetched periodically, and notifications are checked continuously
        
        logger.info("Starting scheduled email calendar notification system...")
        
        # Schedule email processing
        schedule.every(Config.CHECK_INTERVAL_MINUTES).minutes.do(self.process_emails)
        
        # Schedule notification checks (every minute)
        schedule.every(1).minute.do(self.check_and_notify)
        
        logger.info(f"Scheduled email check every {Config.CHECK_INTERVAL_MINUTES} minutes")
        logger.info("Scheduled notification check every 1 minute")
        
        # Keep running
        while True:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check if any tasks need to run every 30 seconds
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in scheduler: {e}", exc_info=True)
                time.sleep(60)  # Wait before retrying
    
    def run_once(self):
        """Run the application once (useful for testing)"""
        logger.info("Running email calendar notification system once...")
        self.process_emails()
        self.check_and_notify()
        logger.info("Single run completed")
    
    def display_upcoming_events(self):
        # Display all upcoming events in the next 24 hours
        events = self.event_manager.get_upcoming_events(hours_ahead=24)
        
        if not events:
            print("\nNo upcoming events in the next 24 hours")
            return
        
        print(f"\n{'='*60}")
        print(f"{'Upcoming Events (Next 24 Hours)':^60}")
        print(f"{'='*60}\n")
        
        for i, event in enumerate(events, 1):
            print(f"{i}. {event['description']}")
            print(f"   Date: {event['event_date']}")
            print(f"   From: {event.get('sender', 'Unknown')}")
            print(f"   Subject: {event.get('email_subject', 'N/A')}")
            print(f"   Confidence: {event['confidence']:.1%}")
            print()
    
    def display_all_events(self):
        # Display all stored events
        events = self.event_manager.get_all_events()
        
        if not events:
            print("\nNo events stored in database")
            return
        
        print(f"\n{'='*60}")
        print(f"{'All Stored Events':^60}")
        print(f"{'='*60}\n")
        
        for i, event in enumerate(events, 1):
            print(f"{i}. {event['description']}")
            print(f"   Date: {event['event_date']}")
            print(f"   From: {event.get('sender', 'Unknown')}")
            print(f"   Notified: {'Yes' if event['is_notified'] else 'No'}")
            print()


def main():
    
    device_tokens = [
        # "your_device_token_1",
        # "your_device_token_2",
    ]
    
    # Initialize the application
    app = EmailCalendarNotifier(device_tokens=device_tokens)
    
    # Run once for testing (comment out to use scheduled version)
    app.run_once()
    app.display_upcoming_events()
    
    # Uncomment to run with scheduled tasks
    app.run_scheduled()


if __name__ == "__main__":
    main()
