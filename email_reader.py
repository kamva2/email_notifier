"""
Email Reader Component
Connects to Outlook/Microsoft 365 and fetches email messages
"""

import logging
from typing import List, Dict, Any
from azure.identity import ClientSecretCredential
import requests
import os

logger = logging.getLogger(__name__)


class EmailReader:
    """Reads emails from Outlook/Microsoft 365"""
    
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        """
        Initialize Outlook email reader
        
        Args:
            tenant_id: Azure tenant ID
            client_id: Azure client ID
            client_secret: Azure client secret
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.authenticate()
    
    def authenticate(self) -> None:
        """Authenticate with Microsoft Graph API"""
        try:
            credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            token = credential.get_token("https://graph.microsoft.com/.default")
            self.token = token.token
            logger.info("Successfully authenticated with Microsoft 365")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    def get_recent_emails(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch recent unread emails from Outlook inbox
        
        Args:
            limit: Number of emails to fetch
            
        Returns:
            List of email dictionaries with subject, body, sender, and received time
        """
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            # Get unread messages
            url = "https://graph.microsoft.com/v1.0/me/mailfolders/inbox/messages"
            params = {
                "$filter": "isRead eq false",
                "$top": limit,
                "$orderby": "receivedDateTime desc"
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            emails = response.json().get("value", [])
            logger.info(f"Fetched {len(emails)} unread emails")
            
            return [
                {
                    "id": email.get("id"),
                    "subject": email.get("subject", ""),
                    "body": email.get("bodyPreview", ""),
                    "full_body": email.get("body", {}).get("content", ""),
                    "sender": email.get("from", {}).get("emailAddress", {}).get("address", ""),
                    "received_time": email.get("receivedDateTime"),
                }
                for email in emails
            ]
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []
    
    def mark_email_as_read(self, email_id: str) -> bool:
        """Mark an email as read"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            url = f"https://graph.microsoft.com/v1.0/me/messages/{email_id}"
            data = {"isRead": True}
            
            response = requests.patch(url, headers=headers, json=data)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error marking email as read: {e}")
            return False
    
    def get_email_by_subject(self, subject: str) -> List[Dict[str, Any]]:
        """Search emails by subject"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            query = f"subject:{subject}"
            url = "https://graph.microsoft.com/v1.0/me/messages"
            params = {
                "$search": f'"{query}"',
                "$top": 10,
                "$orderby": "receivedDateTime desc"
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            emails = response.json().get("value", [])
            logger.info(f"Found {len(emails)} emails matching subject: {subject}")
            
            return [
                {
                    "id": email.get("id"),
                    "subject": email.get("subject", ""),
                    "body": email.get("bodyPreview", ""),
                    "full_body": email.get("body", {}).get("content", ""),
                    "sender": email.get("from", {}).get("emailAddress", {}).get("address", ""),
                    "received_time": email.get("receivedDateTime"),
                }
                for email in emails
            ]
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []
