"""
Simple demonstration of the Observer Pattern in FreshShare Platform
Run this to see the notification system in action
"""
from src.observers.notification_observer import (
    NotificationService,
    EmailNotifier,
    SMSNotifier,
    PushNotifier
)

def main():
    print("=" * 70)
    print("FreshShare Platform - Observer Pattern Demonstration")
    print("=" * 70)
    print()
    
    # Create notification service (Subject)
    notification_service = NotificationService()
    
    # Create observers
    email_notifier = EmailNotifier()
    sms_notifier = SMSNotifier()
    push_notifier = PushNotifier()
    
    print("📌 Step 1: Attaching observers to the notification service")
    notification_service.attach(email_notifier)
    notification_service.attach(sms_notifier)
    notification_service.attach(push_notifier)
    print(f"   ✓ Attached {len(notification_service._observers)} observers\n")
    
    # Simulate a new food listing
    listing_data = {
        'id': 1,
        'vendor_id': 999,  # Vendor ID
        'title': 'Fresh Bread',
        'vendor_name': 'Joe\'s Bakery',
        'quantity': 10,
        'unit': 'loaves',
        'expiry_time': '2025-12-17 18:00:00',
        'pickup_address': '123 Main St, New York',
        'food_type': 'Bakery',
        'latitude': 40.7128,
        'longitude': -74.0060
    }
    
    # Simulate nearby users who should be notified
    nearby_users = [
        {
            'id': 101,
            'name': 'City Food Bank',
            'email': 'contact@cityfoodbank.org',
            'phone': '+1-555-0101',
            'role': 'charity'
        },
        {
            'id': 102,
            'name': 'Community Kitchen',
            'email': 'kitchen@community.org',
            'phone': '+1-555-0102',
            'role': 'charity'
        },
        {
            'id': 103,
            'name': 'John Doe',
            'email': 'john.doe@email.com',
            'phone': '+1-555-0103',
            'role': 'individual'
        }
    ]
    
    print("📌 Step 2: New food listing created!")
    print(f"   📦 {listing_data['title']} - {listing_data['quantity']} {listing_data['unit']}")
    print(f"   🏪 Vendor: {listing_data['vendor_name']}")
    print(f"   📍 Location: {listing_data['pickup_address']}")
    print(f"   ⏰ Expires: {listing_data['expiry_time']}\n")
    
    print("📌 Step 3: Notifying nearby users via Observer pattern")
    print(f"   Found {len(nearby_users)} nearby users\n")
    
    # Notify all nearby users using the Observer pattern
    notification_service.notify(listing_data, nearby_users)
    
    print("=" * 70)
    print("✅ Observer Pattern Demonstration Complete!")
    print("=" * 70)
    print()
    print("Key Benefits Demonstrated:")
    print("  1. ✓ Decoupling: Listing logic doesn't know about notifications")
    print("  2. ✓ Extensibility: Easy to add new notification channels")
    print("  3. ✓ Multiple channels: Email, SMS, and Push notifications")
    print("  4. ✓ Automatic updates: All observers notified automatically")
    print()

if __name__ == "__main__":
    main()
