from flask import Blueprint

portfolio_performance_bp = Blueprint('portfolio_performance', __name__)

from . import routes
