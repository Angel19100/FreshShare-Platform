"""
User routes
"""
from flask import Blueprint

user_bp = Blueprint('users', __name__)


@user_bp.route('/profile', methods=['GET'])
def get_profile():
    return {"message": "User profile endpoint - to be implemented"}
