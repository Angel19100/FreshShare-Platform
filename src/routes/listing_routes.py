"""
Listing routes - API endpoints for food listings
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.services.listing_service import ListingService
from src.models import FoodType
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

listing_bp = Blueprint('listings', __name__)


@listing_bp.route('/', methods=['POST'])
@jwt_required()
def create_listing():
    """
    Create a new food listing
    ---
    tags:
      - Listings
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - quantity
            - unit
            - food_type
            - expiry_time
            - pickup_address
            - latitude
            - longitude
          properties:
            title:
              type: string
              example: "Fresh Bread"
            description:
              type: string
              example: "Whole wheat bread, baked today"
            quantity:
              type: number
              example: 10
            unit:
              type: string
              example: "loaves"
            food_type:
              type: string
              enum: [bakery, produce, dairy, prepared_food, canned_goods, frozen, other]
              example: "bakery"
            expiry_time:
              type: string
              format: date-time
              example: "2025-12-18T20:00:00"
            pickup_address:
              type: string
              example: "123 Main St, City"
            latitude:
              type: number
              example: 40.7128
            longitude:
              type: number
              example: -74.0060
    responses:
      201:
        description: Listing created successfully
      400:
        description: Invalid request data
      401:
        description: Unauthorized
    """
    try:
        vendor_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        required_fields = [
            'title', 'quantity', 'unit', 'food_type', 
            'expiry_time', 'pickup_address', 'latitude', 'longitude'
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Parse expiry time
        try:
            data['expiry_time'] = datetime.fromisoformat(data['expiry_time'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({"error": "Invalid expiry_time format"}), 400
        
        # Parse optional datetime fields
        for field in ['pickup_start_time', 'pickup_end_time']:
            if field in data and data[field]:
                try:
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({"error": f"Invalid {field} format"}), 400
        
        # Validate food type
        try:
            data['food_type'] = FoodType(data['food_type'])
        except ValueError:
            return jsonify({"error": "Invalid food_type"}), 400
        
        # Create listing (this will trigger Observer pattern notifications)
        listing = ListingService.create_listing(vendor_id, data)
        
        return jsonify({
            "message": "Listing created successfully",
            "listing": listing.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating listing: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@listing_bp.route('/search', methods=['GET'])
@jwt_required()
def search_listings():
    """
    Search for food listings near a location
    ---
    tags:
      - Listings
    security:
      - Bearer: []
    parameters:
      - in: query
        name: latitude
        type: number
        required: true
        example: 40.7128
      - in: query
        name: longitude
        type: number
        required: true
        example: -74.0060
      - in: query
        name: radius_km
        type: number
        default: 5.0
        example: 5.0
      - in: query
        name: food_type
        type: string
        enum: [bakery, produce, dairy, prepared_food, canned_goods, frozen, other]
      - in: query
        name: limit
        type: integer
        default: 20
      - in: query
        name: offset
        type: integer
        default: 0
    responses:
      200:
        description: List of nearby food listings
      400:
        description: Invalid parameters
      401:
        description: Unauthorized
    """
    try:
        # Get query parameters
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius_km = request.args.get('radius_km', default=5.0, type=float)
        food_type = request.args.get('food_type', type=str)
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # Validate required parameters
        if latitude is None or longitude is None:
            return jsonify({"error": "latitude and longitude are required"}), 400
        
        # Search listings
        listings = ListingService.search_listings(
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
            food_type=food_type,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            "count": len(listings),
            "listings": [listing.to_dict() for listing in listings]
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching listings: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@listing_bp.route('/<int:listing_id>', methods=['GET'])
@jwt_required()
def get_listing(listing_id):
    """
    Get a specific listing by ID
    ---
    tags:
      - Listings
    security:
      - Bearer: []
    parameters:
      - in: path
        name: listing_id
        type: integer
        required: true
    responses:
      200:
        description: Listing details
      404:
        description: Listing not found
      401:
        description: Unauthorized
    """
    try:
        listing = ListingService.get_listing(listing_id)
        
        if not listing:
            return jsonify({"error": "Listing not found"}), 404
        
        return jsonify({"listing": listing.to_dict()}), 200
        
    except Exception as e:
        logger.error(f"Error getting listing: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@listing_bp.route('/<int:listing_id>', methods=['PUT'])
@jwt_required()
def update_listing(listing_id):
    """
    Update a listing (vendor only)
    ---
    tags:
      - Listings
    security:
      - Bearer: []
    parameters:
      - in: path
        name: listing_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            quantity:
              type: number
            status:
              type: string
    responses:
      200:
        description: Listing updated successfully
      403:
        description: Not authorized to update this listing
      404:
        description: Listing not found
    """
    try:
        vendor_id = get_jwt_identity()
        listing = ListingService.get_listing(listing_id)
        
        if not listing:
            return jsonify({"error": "Listing not found"}), 404
        
        # Check if user is the owner
        if listing.vendor_id != vendor_id:
            return jsonify({"error": "Not authorized to update this listing"}), 403
        
        data = request.get_json()
        updated_listing = ListingService.update_listing(listing_id, data)
        
        return jsonify({
            "message": "Listing updated successfully",
            "listing": updated_listing.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating listing: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@listing_bp.route('/<int:listing_id>', methods=['DELETE'])
@jwt_required()
def delete_listing(listing_id):
    """
    Delete a listing (vendor only)
    ---
    tags:
      - Listings
    security:
      - Bearer: []
    parameters:
      - in: path
        name: listing_id
        type: integer
        required: true
    responses:
      200:
        description: Listing deleted successfully
      403:
        description: Not authorized to delete this listing
      404:
        description: Listing not found
    """
    try:
        vendor_id = get_jwt_identity()
        listing = ListingService.get_listing(listing_id)
        
        if not listing:
            return jsonify({"error": "Listing not found"}), 404
        
        # Check if user is the owner
        if listing.vendor_id != vendor_id:
            return jsonify({"error": "Not authorized to delete this listing"}), 403
        
        ListingService.delete_listing(listing_id)
        
        return jsonify({"message": "Listing deleted successfully"}), 200
        
    except Exception as e:
        logger.error(f"Error deleting listing: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@listing_bp.route('/my-listings', methods=['GET'])
@jwt_required()
def get_my_listings():
    """
    Get all listings for the authenticated vendor
    ---
    tags:
      - Listings
    security:
      - Bearer: []
    parameters:
      - in: query
        name: status
        type: string
        enum: [available, claimed, completed, expired, cancelled]
    responses:
      200:
        description: List of vendor's listings
      401:
        description: Unauthorized
    """
    try:
        vendor_id = get_jwt_identity()
        status = request.args.get('status', type=str)
        
        listings = ListingService.get_vendor_listings(vendor_id, status)
        
        return jsonify({
            "count": len(listings),
            "listings": [listing.to_dict() for listing in listings]
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting vendor listings: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
