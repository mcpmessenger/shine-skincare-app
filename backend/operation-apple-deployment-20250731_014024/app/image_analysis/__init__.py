from flask import Blueprint

image_bp = Blueprint('image_analysis', __name__)

from . import routes 