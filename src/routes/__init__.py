"""
Routes package initialization
"""
from src.routes.auth_routes import auth_bp
from src.routes.listing_routes import listing_bp
from src.routes.claim_routes import claim_bp
from src.routes.user_routes import user_bp

__all__ = ['auth_bp', 'listing_bp', 'claim_bp', 'user_bp']
