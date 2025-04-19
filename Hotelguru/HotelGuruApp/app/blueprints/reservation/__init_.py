from apiflask import APIBlueprint

bp = APIBlueprint('reservation', __name__, tag="reservation")

from app.blueprints.reservation import routes