from flask import Blueprint

data_bp = Blueprint('data', __name__)

from . import models, repositories