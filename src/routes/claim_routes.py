"""
Claim routes
"""
from flask import Blueprint

claim_bp = Blueprint('claims', __name__)


@claim_bp.route('/', methods=['GET'])
def get_claims():
    return {"message": "Claims endpoint - to be implemented"}
