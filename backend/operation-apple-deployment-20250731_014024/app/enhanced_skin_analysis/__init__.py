from flask import Blueprint

enhanced_skin_bp = Blueprint('enhanced_skin', __name__)

from . import routes 