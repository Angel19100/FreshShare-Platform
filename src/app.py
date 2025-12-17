"""
Main Flask application for Fresh-Share Platform
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from src.config import config
from src.models import db
from src.routes.auth_routes import auth_bp
from src.routes.listing_routes import listing_bp
from src.routes.claim_routes import claim_bp
from src.routes.user_routes import user_bp
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name='development'):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration to use (development, testing, production)
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    JWTManager(app)
    
    # Initialize Swagger for API documentation
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs"
    }
    
    swagger_template = {
        "info": {
            "title": "Fresh-Share Platform API",
            "description": "Hyperlocal Food Waste Exchange Platform API",
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
            }
        }
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(listing_bp, url_prefix='/api/listings')
    app.register_blueprint(claim_bp, url_prefix='/api/claims')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "service": "Fresh-Share Platform"
        }), 200
    
    # Root endpoint
    @app.route('/')
    def index():
        """Root endpoint"""
        return jsonify({
            "message": "Welcome to Fresh-Share Platform API",
            "version": "1.0.0",
            "documentation": "/api/docs"
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({"error": "Internal server error"}), 500
    
    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")
    
    logger.info(f"Application created with config: {config_name}")
    
    return app


if __name__ == '__main__':
    import os

    app = create_app(os.getenv('FLASK_CONFIG', 'development'))

    # Read host/port from environment with sensible defaults
    host = os.getenv('HOST', '0.0.0.0')
    try:
        port = int(os.getenv('PORT', '5000'))
    except ValueError:
        port = 5000

    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('1', 'true', 'yes')

    app.run(host=host, port=port, debug=debug)
