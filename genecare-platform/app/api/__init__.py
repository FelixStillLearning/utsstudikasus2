from flask import Blueprint

api_bp = Blueprint('api', __name__)
api = api_bp

from . import routes