"""
Authentication routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from src.models import db, User, UserRole
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
            - name
            - role
          properties:
            email:
              type: string
              example: "vendor@example.com"
            password:
              type: string
              example: "password123"
            name:
              type: string
              example: "Fresh Bakery"
            role:
              type: string
              enum: [vendor, charity, individual]
              example: "vendor"
            phone:
              type: string
              example: "+1234567890"
            address:
              type: string
              example: "123 Main St"
            latitude:
              type: number
              example: 40.7128
            longitude:
              type: number
              example: -74.0060
    responses:
      201:
        description: User registered successfully
      400:
        description: Invalid request or user already exists
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "User already exists"}), 400
        
        # Validate role
        try:
            role = UserRole(data['role'])
        except ValueError:
            return jsonify({"error": "Invalid role"}), 400
        
        # Create user
        user = User(
            email=data['email'],
            name=data['name'],
            role=role,
            phone=data.get('phone'),
            address=data.get('address'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        user.set_password(data['password'])
        
        # Set location if coordinates provided
        if user.latitude and user.longitude:
            user.location = f"POINT({user.longitude} {user.latitude})"
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User registered: {user.email}")
        
        return jsonify({
            "message": "User registered successfully",
            "user": user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login and get JWT token
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: "vendor@example.com"
            password:
              type: string
              example: "password123"
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'email' not in data or 'password' not in data:
            return jsonify({"error": "Email and password required"}), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({"error": "Invalid credentials"}), 401
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        logger.info(f"User logged in: {user.email}")
        
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
