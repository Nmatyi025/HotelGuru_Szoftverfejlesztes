from apiflask import APIBlueprint

bp = APIBlueprint('main', __name__, tag="Main")

from app.main import routes
from app.models import *
