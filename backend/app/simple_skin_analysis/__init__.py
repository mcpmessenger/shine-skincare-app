from flask import Blueprint

simple_skin_bp = Blueprint('simple_skin', __name__)

from . import routes 