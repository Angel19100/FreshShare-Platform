"""
Observer Pattern Implementation for Notification System
This implements the Observer design pattern to notify users about new food listings.
"""
from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Observer(ABC):
    """
    Abstract Observer class
    All concrete observers must implement the update method
    """
    
    @abstractmethod
    def update(self, listing_data: dict, user_data: dict):
        """
        Called when a new listing is available
        
        Args:
            listing_data: Dictionary containing listing information
            user_data: Dictionary containing user information to notify
        """
        pass


class EmailNotifier(Observer):
    """
    Concrete Observer - Sends email notifications
    """
    
    def update(self, listing_data: dict, user_data: dict):
        """Send email notification to user"""
        try:
            # In production, integrate with email service (SendGrid, AWS SES, etc.)
            logger.info(
                f"[EMAIL] Sending notification to {user_data['email']}: "
                f"New listing '{listing_data['title']}' available nearby"
            )
            
            # Simulate email sending
            email_body = self._compose_email(listing_data, user_data)
            # send_email(to=user_data['email'], subject="New Food Available Nearby", body=email_body)
            
            logger.info(f"Email notification sent successfully to {user_data['email']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False
    
    def _compose_email(self, listing_data: dict, user_data: dict) -> str:
        """Compose email body"""
        return f"""
        Hello {user_data['name']},
        
        A new food listing is available near you!
        
        Title: {listing_data['title']}
        Quantity: {listing_data['quantity']} {listing_data['unit']}
        Location: {listing_data['pickup_address']}
        Available until: {listing_data['expiry_time']}
        
        Log in to Fresh-Share to claim this food before it expires.
        
        Best regards,
        Fresh-Share Team
        """


class SMSNotifier(Observer):
    """
    Concrete Observer - Sends SMS notifications
    """
    
    def update(self, listing_data: dict, user_data: dict):
        """Send SMS notification to user"""
        try:
            if not user_data.get('phone'):
                logger.warning(f"User {user_data['email']} has no phone number")
                return False
            
            # In production, integrate with SMS service (Twilio, AWS SNS, etc.)
            logger.info(
                f"[SMS] Sending notification to {user_data['phone']}: "
                f"New listing '{listing_data['title']}' available nearby"
            )
            
            # Simulate SMS sending
            sms_message = self._compose_sms(listing_data)
            # send_sms(to=user_data['phone'], message=sms_message)
            
            logger.info(f"SMS notification sent successfully to {user_data['phone']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {str(e)}")
            return False
    
    def _compose_sms(self, listing_data: dict) -> str:
        """Compose SMS message"""
        return (
            f"Fresh-Share: {listing_data['title']} available nearby! "
            f"{listing_data['quantity']} {listing_data['unit']}. "
            f"Claim now before {listing_data['expiry_time']}"
        )


class PushNotifier(Observer):
    """
    Concrete Observer - Sends push notifications (for mobile apps)
    """
    
    def update(self, listing_data: dict, user_data: dict):
        """Send push notification to user"""
        try:
            # In production, integrate with push notification service (FCM, APNS, etc.)
            logger.info(
                f"[PUSH] Sending notification to user {user_data['id']}: "
                f"New listing '{listing_data['title']}' available nearby"
            )
            
            # Simulate push notification
            push_payload = self._compose_push(listing_data)
            # send_push_notification(user_id=user_data['id'], payload=push_payload)
            
            logger.info(f"Push notification sent successfully to user {user_data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            return False
    
    def _compose_push(self, listing_data: dict) -> dict:
        """Compose push notification payload"""
        return {
            "title": "New Food Available Nearby!",
            "body": f"{listing_data['title']} - {listing_data['quantity']} {listing_data['unit']}",
            "data": {
                "listing_id": listing_data['id'],
                "type": "new_listing"
            }
        }


class NotificationService:
    """
    Subject class that manages observers and sends notifications
    This is the core of the Observer pattern implementation
    """
    
    def __init__(self):
        """Initialize notification service with empty observer list"""
        self._observers: List[Observer] = []
        logger.info("NotificationService initialized")
    
    def attach(self, observer: Observer):
        """
        Attach an observer to the notification service
        
        Args:
            observer: Observer instance to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)
            logger.info(f"Attached observer: {observer.__class__.__name__}")
    
    def detach(self, observer: Observer):
        """
        Detach an observer from the notification service
        
        Args:
            observer: Observer instance to detach
        """
        if observer in self._observers:
            self._observers.remove(observer)
            logger.info(f"Detached observer: {observer.__class__.__name__}")
    
    def notify(self, listing_data: dict, nearby_users: List[dict]):
        """
        Notify all observers about a new listing
        
        Args:
            listing_data: Dictionary containing listing information
            nearby_users: List of user dictionaries who should be notified
        """
        logger.info(
            f"Notifying {len(nearby_users)} users about new listing: {listing_data['title']}"
        )
        
        notification_count = 0
        
        for user_data in nearby_users:
            # Skip the vendor who created the listing
            if user_data['id'] == listing_data['vendor_id']:
                continue
            
            # Notify all attached observers for this user
            for observer in self._observers:
                try:
                    success = observer.update(listing_data, user_data)
                    if success:
                        notification_count += 1
                except Exception as e:
                    logger.error(
                        f"Error notifying user {user_data['id']} via {observer.__class__.__name__}: {str(e)}"
                    )
        
        logger.info(f"Sent {notification_count} notifications successfully")
        return notification_count
    
    def get_observer_count(self) -> int:
        """Get the number of attached observers"""
        return len(self._observers)


# Singleton instance of notification service
notification_service = NotificationService()

# Attach all observers by default
notification_service.attach(EmailNotifier())
notification_service.attach(SMSNotifier())
notification_service.attach(PushNotifier())
