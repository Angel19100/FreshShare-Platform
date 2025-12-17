"""
Listing service - Business logic for food listings
Integrates with Observer pattern for notifications
"""
from datetime import datetime, timezone
from typing import List, Optional, Dict
from sqlalchemy import func, and_
from geoalchemy2.functions import ST_DWithin, ST_MakePoint
from src.models import db, FoodListing, User, ListingStatus, UserRole
from src.observers.notification_observer import notification_service
import logging

logger = logging.getLogger(__name__)


class ListingService:
    """Service class for managing food listings"""
    
    @staticmethod
    def create_listing(vendor_id: int, listing_data: dict) -> FoodListing:
        """
        Create a new food listing and notify nearby users (Observer pattern)
        
        Args:
            vendor_id: ID of the vendor creating the listing
            listing_data: Dictionary containing listing information
            
        Returns:
            Created FoodListing object
        """
        try:
            # Validate vendor exists and has correct role
            vendor = User.query.get(vendor_id)
            if not vendor or vendor.role != UserRole.VENDOR:
                raise ValueError("Invalid vendor")
            
            # Create listing
            listing = FoodListing(
                vendor_id=vendor_id,
                title=listing_data['title'],
                description=listing_data.get('description'),
                quantity=listing_data['quantity'],
                unit=listing_data['unit'],
                food_type=listing_data['food_type'],
                expiry_time=listing_data['expiry_time'],
                pickup_start_time=listing_data.get('pickup_start_time'),
                pickup_end_time=listing_data.get('pickup_end_time'),
                pickup_address=listing_data['pickup_address'],
                latitude=listing_data['latitude'],
                longitude=listing_data['longitude'],
                image_url=listing_data.get('image_url'),
                special_instructions=listing_data.get('special_instructions'),
                status=ListingStatus.AVAILABLE
            )
            
            # Set geospatial location
            listing.location = f"POINT({listing.longitude} {listing.latitude})"
            
            # Save to database
            db.session.add(listing)
            db.session.commit()
            
            logger.info(f"Created listing: {listing.id} - {listing.title}")
            
            # Notify nearby users using Observer pattern
            ListingService._notify_nearby_users(listing)
            
            return listing
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating listing: {str(e)}")
            raise
    
    @staticmethod
    def _notify_nearby_users(listing: FoodListing):
        """
        Find nearby users and notify them about the new listing
        This method triggers the Observer pattern
        
        Args:
            listing: The newly created FoodListing
        """
        try:
            # Find users within search radius (excluding the vendor)
            nearby_users = ListingService.find_nearby_users(
                latitude=listing.latitude,
                longitude=listing.longitude,
                radius_km=5.0,  # Default 5km radius
                exclude_user_id=listing.vendor_id
            )
            
            if not nearby_users:
                logger.info("No nearby users found to notify")
                return
            
            # Prepare listing data for notification
            listing_data = listing.to_dict()
            
            # Prepare user data for notification
            users_data = [user.to_dict() for user in nearby_users]
            
            # Trigger Observer pattern - notify all observers
            notification_service.notify(listing_data, users_data)
            
        except Exception as e:
            logger.error(f"Error notifying nearby users: {str(e)}")
    
    @staticmethod
    def find_nearby_users(
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        exclude_user_id: Optional[int] = None
    ) -> List[User]:
        """
        Find users within a certain radius using geospatial query
        
        Args:
            latitude: Latitude of the center point
            longitude: Longitude of the center point
            radius_km: Search radius in kilometers
            exclude_user_id: User ID to exclude from results
            
        Returns:
            List of User objects within the radius
        """
        try:
            # Create a point for the location
            point = ST_MakePoint(longitude, latitude)
            
            # Build query
            query = User.query.filter(
                User.location.isnot(None),
                ST_DWithin(
                    User.location,
                    point,
                    radius_km * 1000  # Convert km to meters
                )
            )
            
            # Exclude specific user if provided
            if exclude_user_id:
                query = query.filter(User.id != exclude_user_id)
            
            # Only notify verified users
            query = query.filter(User.verified == True)
            
            users = query.all()
            logger.info(f"Found {len(users)} nearby users within {radius_km}km")
            
            return users
            
        except Exception as e:
            logger.error(f"Error finding nearby users: {str(e)}")
            return []
    
    @staticmethod
    def search_listings(
        latitude: float,
        longitude: float,
        radius_km: float = 5.0,
        food_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[FoodListing]:
        """
        Search for available food listings near a location
        
        Args:
            latitude: Latitude of the search center
            longitude: Longitude of the search center
            radius_km: Search radius in kilometers
            food_type: Optional filter by food type
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of FoodListing objects
        """
        try:
            # Create a point for the location
            point = ST_MakePoint(longitude, latitude)
            
            # Build query
            query = FoodListing.query.filter(
                FoodListing.status == ListingStatus.AVAILABLE,
                FoodListing.expiry_time > datetime.now(timezone.utc),
                ST_DWithin(
                    FoodListing.location,
                    point,
                    radius_km * 1000  # Convert km to meters
                )
            )
            
            # Filter by food type if provided
            if food_type:
                query = query.filter(FoodListing.food_type == food_type)
            
            # Order by creation date (newest first)
            query = query.order_by(FoodListing.created_at.desc())
            
            # Apply pagination
            listings = query.limit(limit).offset(offset).all()
            
            logger.info(f"Found {len(listings)} listings within {radius_km}km")
            
            return listings
            
        except Exception as e:
            logger.error(f"Error searching listings: {str(e)}")
            return []
    
    @staticmethod
    def get_listing(listing_id: int) -> Optional[FoodListing]:
        """Get a listing by ID"""
        return FoodListing.query.get(listing_id)
    
    @staticmethod
    def update_listing(listing_id: int, update_data: dict) -> FoodListing:
        """Update an existing listing"""
        try:
            listing = FoodListing.query.get(listing_id)
            if not listing:
                raise ValueError("Listing not found")
            
            # Update allowed fields
            allowed_fields = [
                'title', 'description', 'quantity', 'unit', 'food_type',
                'expiry_time', 'pickup_start_time', 'pickup_end_time',
                'special_instructions', 'status'
            ]
            
            for field in allowed_fields:
                if field in update_data:
                    setattr(listing, field, update_data[field])
            
            db.session.commit()
            logger.info(f"Updated listing: {listing_id}")
            
            return listing
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating listing: {str(e)}")
            raise
    
    @staticmethod
    def delete_listing(listing_id: int) -> bool:
        """Delete a listing (soft delete by marking as cancelled)"""
        try:
            listing = FoodListing.query.get(listing_id)
            if not listing:
                raise ValueError("Listing not found")
            
            listing.status = ListingStatus.CANCELLED
            db.session.commit()
            
            logger.info(f"Deleted listing: {listing_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting listing: {str(e)}")
            raise
    
    @staticmethod
    def get_vendor_listings(vendor_id: int, status: Optional[str] = None) -> List[FoodListing]:
        """Get all listings for a vendor"""
        query = FoodListing.query.filter(FoodListing.vendor_id == vendor_id)
        
        if status:
            query = query.filter(FoodListing.status == status)
        
        return query.order_by(FoodListing.created_at.desc()).all()
