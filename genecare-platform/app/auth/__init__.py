from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
auth = auth_bp

from . import routes, models, utils