"""
Database models for Fresh-Share Platform
"""
from datetime import datetime, timezone
from enum import Enum as PyEnum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, Float, CheckConstraint, Text, event
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Helper function to get location column type based on database
def get_location_column():
    """Return appropriate column type for location based on database"""
    try:
        from geoalchemy2 import Geography
        # Will use Geography for PostgreSQL, Text will be used at runtime for SQLite
        return Geography(geometry_type="POINT", srid=4326)
    except ImportError:
        return Text


class UserRole(PyEnum):
    """User role enumeration"""
    VENDOR = "vendor"
    CHARITY = "charity"
    INDIVIDUAL = "individual"
    ADMIN = "admin"


class ListingStatus(PyEnum):
    """Listing status enumeration"""
    AVAILABLE = "available"
    CLAIMED = "claimed"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class FoodType(PyEnum):
    """Food type enumeration"""
    BAKERY = "bakery"
    PRODUCE = "produce"
    DAIRY = "dairy"
    PREPARED_FOOD = "prepared_food"
    CANNED_GOODS = "canned_goods"
    FROZEN = "frozen"
    OTHER = "other"


class ClaimStatus(PyEnum):
    """Claim status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PICKED_UP = "picked_up"
    CANCELLED = "cancelled"


class User(db.Model):
    """User model - Base class for all user types"""
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(Enum(UserRole), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    
    # Geospatial data - stored as TEXT in SQLite for testing
    location = db.Column(Text, nullable=True)
    latitude = db.Column(Float)
    longitude = db.Column(Float)
    
    # Verification and ratings
    verified = db.Column(db.Boolean, default=False)
    rating = db.Column(Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    listings = db.relationship("FoodListing", back_populates="vendor", lazy="dynamic")
    claims = db.relationship("Claim", back_populates="claimer", lazy="dynamic")
    ratings_given = db.relationship(
        "Rating", foreign_keys="Rating.rater_id", back_populates="rater", lazy="dynamic"
    )
    ratings_received = db.relationship(
        "Rating", foreign_keys="Rating.rated_id", back_populates="rated", lazy="dynamic"
    )
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role.value,
            "name": self.name,
            "phone": self.phone,
            "address": self.address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "verified": self.verified,
            "rating": round(self.rating, 2),
            "rating_count": self.rating_count,
            "created_at": self.created_at.isoformat(),
        }
    
    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"


class FoodListing(db.Model):
    """Food listing model - Subject in Observer pattern"""
    __tablename__ = "food_listings"
    
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Listing details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)  # kg, pieces, servings, etc.
    food_type = db.Column(Enum(FoodType), nullable=False)
    
    # Time information
    expiry_time = db.Column(db.DateTime, nullable=False)
    pickup_start_time = db.Column(db.DateTime)
    pickup_end_time = db.Column(db.DateTime)
    
    # Location
    pickup_address = db.Column(db.String(255), nullable=False)
    location = db.Column(Text, nullable=True)
    latitude = db.Column(Float, nullable=False)
    longitude = db.Column(Float, nullable=False)
    
    # Status
    status = db.Column(Enum(ListingStatus), default=ListingStatus.AVAILABLE)
    
    # Additional info
    image_url = db.Column(db.String(500))
    special_instructions = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    vendor = db.relationship("User", back_populates="listings")
    claims = db.relationship("Claim", back_populates="listing", lazy="dynamic")
    
    __table_args__ = (
        CheckConstraint("quantity > 0", name="positive_quantity"),
        CheckConstraint("expiry_time > created_at", name="valid_expiry_time"),
    )
    
    def to_dict(self):
        """Convert listing to dictionary"""
        return {
            "id": self.id,
            "vendor_id": self.vendor_id,
            "vendor_name": self.vendor.name,
            "title": self.title,
            "description": self.description,
            "quantity": self.quantity,
            "unit": self.unit,
            "food_type": self.food_type.value,
            "expiry_time": self.expiry_time.isoformat(),
            "pickup_start_time": self.pickup_start_time.isoformat() if self.pickup_start_time else None,
            "pickup_end_time": self.pickup_end_time.isoformat() if self.pickup_end_time else None,
            "pickup_address": self.pickup_address,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "status": self.status.value,
            "image_url": self.image_url,
            "special_instructions": self.special_instructions,
            "created_at": self.created_at.isoformat(),
        }
    
    def __repr__(self):
        return f"<FoodListing {self.title} by {self.vendor.name}>"


class Claim(db.Model):
    """Claim model - Represents a claim on a food listing"""
    __tablename__ = "claims"
    
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey("food_listings.id"), nullable=False)
    claimer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # Claim details
    status = db.Column(Enum(ClaimStatus), default=ClaimStatus.PENDING)
    notes = db.Column(db.Text)
    
    # Timestamps
    claimed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    confirmed_at = db.Column(db.DateTime)
    picked_up_at = db.Column(db.DateTime)
    cancelled_at = db.Column(db.DateTime)
    
    # Relationships
    listing = db.relationship("FoodListing", back_populates="claims")
    claimer = db.relationship("User", back_populates="claims")
    
    def to_dict(self):
        """Convert claim to dictionary"""
        return {
            "id": self.id,
            "listing_id": self.listing_id,
            "claimer_id": self.claimer_id,
            "claimer_name": self.claimer.name,
            "status": self.status.value,
            "notes": self.notes,
            "claimed_at": self.claimed_at.isoformat(),
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
            "picked_up_at": self.picked_up_at.isoformat() if self.picked_up_at else None,
        }
    
    def __repr__(self):
        return f"<Claim {self.id} for Listing {self.listing_id}>"


class Rating(db.Model):
    """Rating model - Allows users to rate each other"""
    __tablename__ = "ratings"
    
    id = db.Column(db.Integer, primary_key=True)
    rater_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rated_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("food_listings.id"))
    
    score = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    rater = db.relationship("User", foreign_keys=[rater_id], back_populates="ratings_given")
    rated = db.relationship("User", foreign_keys=[rated_id], back_populates="ratings_received")
    
    __table_args__ = (
        CheckConstraint("score >= 1 AND score <= 5", name="valid_score"),
        CheckConstraint("rater_id != rated_id", name="cannot_rate_self"),
    )
    
    def to_dict(self):
        """Convert rating to dictionary"""
        return {
            "id": self.id,
            "rater_id": self.rater_id,
            "rater_name": self.rater.name,
            "rated_id": self.rated_id,
            "listing_id": self.listing_id,
            "score": self.score,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
        }
    
    def __repr__(self):
        return f"<Rating {self.score}/5 from User {self.rater_id} to User {self.rated_id}>"
