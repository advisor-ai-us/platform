from flask import Blueprint

stock_recommendations_bp = Blueprint('stock_recommendations', __name__)

from . import routes
