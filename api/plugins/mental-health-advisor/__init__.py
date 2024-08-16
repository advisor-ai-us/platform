from flask import Blueprint

mental_health_bp = Blueprint('mental_health', __name__)

from . import routes
