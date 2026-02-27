"""
Outlook Service - Integration with Microsoft Outlook via Microsoft Graph API
"""
import logging
from typing import Optional, List
from datetime import datetime

from azure.identity import ClientSecretCredential
from msgraph.core import GraphClient

from app.config import settings

logger = logging.getLogger(__name__)


class OutlookService:
    """Service for Outlook integration"""

    def __init__(self):
        self.graph_client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Microsoft Graph client"""
        if not all(
            [
                settings.OUTLOOK_CLIENT_ID,
                settings.OUTLOOK_CLIENT_SECRET,
                settings.OUTLOOK_TENANT_ID,
            ]
        ):
            logger.warning("Outlook credentials not configured")
            return

        try:
            credentials = ClientSecretCredential(
                tenant_id=settings.OUTLOOK_TENANT_ID,
                client_id=settings.OUTLOOK_CLIENT_ID,
                client_secret=settings.OUTLOOK_CLIENT_SECRET,
            )
            self.graph_client = GraphClient(credential=credentials)
            logger.info("Microsoft Graph client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Microsoft Graph client: {e}")

    def is_configured(self) -> bool:
        """Check if Outlook is configured"""
        return self.graph_client is not None

    async def get_emails(
        self,
        limit: int = 10,
        skip: int = 0,
        filter_query: Optional[str] = None,
    ) -> List[dict]:
        """
        Get emails from Outlook

        Args:
            limit: Number of emails to fetch
            skip: Number of emails to skip
            filter_query: Optional filter query for emails

        Returns:
            List of emails with metadata
        """
        if not self.is_configured():
            logger.error("Outlook not configured")
            return []

        try:
            query = "/me/messages"

            # Build query parameters
            params = {
                "$top": limit,
                "$skip": skip,
                "$select": "id,from,subject,bodyPreview,receivedDateTime,body",
                "$orderby": "receivedDateTime desc",
            }

            if filter_query:
                params["$filter"] = filter_query

            response = self.graph_client.get(query, params=params)
            emails = response.get("value", [])

            return [self._format_email(email) for email in emails]

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []

    def _format_email(self, email: dict) -> dict:
        """Format email response"""
        return {
            "outlook_id": email.get("id"),
            "sender": email.get("from", {}).get("emailAddress", {}).get("address", ""),
            "subject": email.get("subject", ""),
            "body": email.get("body", {}).get("content", ""),
            "body_preview": email.get("bodyPreview", ""),
            "received_at": email.get("receivedDateTime"),
        }

    async def get_email_detail(self, email_id: str) -> Optional[dict]:
        """
        Get detailed email information

        Args:
            email_id: Outlook email ID

        Returns:
            Detailed email information
        """
        if not self.is_configured():
            logger.error("Outlook not configured")
            return None

        try:
            query = f"/me/messages/{email_id}"
            params = {
                "$select": "id,from,subject,bodyPreview,receivedDateTime,body,conversationId"
            }

            response = self.graph_client.get(query, params=params)
            return self._format_email(response)

        except Exception as e:
            logger.error(f"Error fetching email detail: {e}")
            return None

    async def send_reply(
        self, email_id: str, reply_body: str, reply_subject: Optional[str] = None
    ) -> bool:
        """
        Send reply to email

        Args:
            email_id: Outlook email ID to reply to
            reply_body: Reply message body
            reply_subject: Optional reply subject

        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured():
            logger.error("Outlook not configured")
            return False

        try:
            query = f"/me/messages/{email_id}/reply"

            payload = {
                "comment": reply_body,
            }

            self.graph_client.post(query, data=payload)
            logger.info(f"Reply sent to email {email_id}")
            return True

        except Exception as e:
            logger.error(f"Error sending reply: {e}")
            return False

    async def forward_email(
        self, email_id: str, to_recipients: List[str], comment: Optional[str] = None
    ) -> bool:
        """
        Forward email to recipients

        Args:
            email_id: Outlook email ID to forward
            to_recipients: List of recipient email addresses
            comment: Optional comment to include

        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured():
            logger.error("Outlook not configured")
            return False

        try:
            query = f"/me/messages/{email_id}/forward"

            payload = {
                "toRecipients": [
                    {"emailAddress": {"address": recipient}} for recipient in to_recipients
                ],
                "comment": comment or "",
            }

            self.graph_client.post(query, data=payload)
            logger.info(f"Email {email_id} forwarded to {len(to_recipients)} recipients")
            return True

        except Exception as e:
            logger.error(f"Error forwarding email: {e}")
            return False

    async def mark_as_read(self, email_id: str) -> bool:
        """
        Mark email as read

        Args:
            email_id: Outlook email ID

        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured():
            logger.error("Outlook not configured")
            return False

        try:
            query = f"/me/messages/{email_id}"
            payload = {"isRead": True}

            self.graph_client.patch(query, data=payload)
            logger.info(f"Email {email_id} marked as read")
            return True

        except Exception as e:
            logger.error(f"Error marking email as read: {e}")
            return False

    async def search_emails(self, search_query: str, limit: int = 20) -> List[dict]:
        """
        Search emails

        Args:
            search_query: Search query string
            limit: Maximum number of results

        Returns:
            List of matching emails
        """
        if not self.is_configured():
            logger.error("Outlook not configured")
            return []

        try:
            query = "/me/messages"
            params = {
                "$search": f'"{search_query}"',
                "$top": limit,
                "$select": "id,from,subject,bodyPreview,receivedDateTime",
            }

            response = self.graph_client.get(query, params=params)
            emails = response.get("value", [])

            return [self._format_email(email) for email in emails]

        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []

    async def get_unread_emails(self, limit: int = 20) -> List[dict]:
        """
        Get unread emails

        Args:
            limit: Maximum number of unread emails

        Returns:
            List of unread emails
        """
        return await self.get_emails(
            limit=limit, filter_query='isRead eq false'
        )


# Singleton instance
_outlook_service: Optional[OutlookService] = None


def get_outlook_service() -> OutlookService:
    """Get or create Outlook service instance"""
    global _outlook_service
    if _outlook_service is None:
        _outlook_service = OutlookService()
    return _outlook_service
