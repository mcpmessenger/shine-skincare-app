from flask import Blueprint

enhanced_image_bp = Blueprint('enhanced_image', __name__)
 
from . import routes 