"""
Notification System Component
Sends reminders to phone via Firebase Cloud Messaging (FCM)
"""

import logging
from typing import Dict, Any, List, Optional
import firebase_admin
from firebase_admin import credentials, messaging
import os

logger = logging.getLogger(__name__)


class NotificationSystem:
    """Sends push notifications via Firebase Cloud Messaging"""
    
    def __init__(self, credentials_path: str):
        """
        Initialize Firebase Cloud Messaging
        
        Args:
            credentials_path: Path to Firebase admin SDK credentials JSON file
        """
        if not os.path.exists(credentials_path):
            logger.error(f"Firebase credentials not found at {credentials_path}")
            raise FileNotFoundError(f"Firebase credentials not found at {credentials_path}")
        
        try:
            if not firebase_admin._apps:
                creds = credentials.Certificate(credentials_path)
                firebase_admin.initialize_app(creds)
            logger.info("Firebase Cloud Messaging initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    def send_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Send a push notification to a device
        
        Args:
            device_token: FCM device token
            title: Notification title
            body: Notification body/message
            data: Additional data to send (optional)
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=device_token
            )
            
            response = messaging.send(message)
            logger.info(f"Notification sent successfully: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False
    
    def send_topic_notification(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Send a push notification to all devices subscribed to a topic
        
        Args:
            topic: FCM topic name
            title: Notification title
            body: Notification body/message
            data: Additional data to send (optional)
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                topic=topic
            )
            
            response = messaging.send(message)
            logger.info(f"Topic notification sent to {topic}: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to send topic notification: {e}")
            return False
    
    def send_multicast_notification(
        self,
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send notifications to multiple devices
        
        Args:
            device_tokens: List of FCM device tokens
            title: Notification title
            body: Notification body/message
            data: Additional data to send (optional)
            
        Returns:
            Dictionary with success count and failed tokens
        """
        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=device_tokens
            )
            
            response = messaging.send_multicast(message)
            
            logger.info(f"Multicast sent: {response.success_count} succeeded, {response.failure_count} failed")
            
            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "failed_tokens": [
                    device_tokens[idx] for idx, send_resp in enumerate(response.responses)
                    if not send_resp.success
                ]
            }
        except Exception as e:
            logger.error(f"Failed to send multicast notification: {e}")
            return {
                "success_count": 0,
                "failure_count": len(device_tokens),
                "failed_tokens": device_tokens,
                "error": str(e)
            }
    
    def send_event_notification(
        self,
        device_token: str,
        event: Dict[str, Any]
    ) -> bool:
        """
        Send a formatted event notification
        
        Args:
            device_token: FCM device token
            event: Event dictionary
            
        Returns:
            True if notification sent successfully
        """
        from datetime import datetime
        
        try:
            event_date = datetime.fromisoformat(event['event_date'])
            formatted_date = event_date.strftime("%d %b %Y at %H:%M")
            
            title = "📅 Calendar Reminder"
            body = f"{event['description']}\n{formatted_date}"
            
            if event.get('email_subject'):
                body += f"\n(from: {event['email_subject']})"
            
            data = {
                "event_id": str(event.get('id', '')),
                "event_date": event['event_date'],
                "confidence": str(event.get('confidence', 0)),
            }
            
            return self.send_notification(device_token, title, body, data)
        except Exception as e:
            logger.error(f"Failed to send event notification: {e}")
            return False
    
    def subscribe_to_topic(self, device_tokens: List[str], topic: str) -> bool:
        """
        Subscribe devices to a topic
        
        Args:
            device_tokens: List of device tokens to subscribe
            topic: Topic name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = messaging.make_topic_management_request(
                device_tokens,
                "iid/subscribe",
                topic
            )
            logger.info(f"Subscribed to topic {topic}: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to topic: {e}")
            return False
    
    def unsubscribe_from_topic(self, device_tokens: List[str], topic: str) -> bool:
        """
        Unsubscribe devices from a topic
        
        Args:
            device_tokens: List of device tokens to unsubscribe
            topic: Topic name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = messaging.make_topic_management_request(
                device_tokens,
                "iid/unsubscribe",
                topic
            )
            logger.info(f"Unsubscribed from topic {topic}: {response}")
            return True
        except Exception as e:
            logger.error(f"Failed to unsubscribe from topic: {e}")
            return False
