from apiflask import APIBlueprint

bp = APIBlueprint('reservation', __name__, tag="Reservation")

# Import routes to register them with the blueprint
from app.blueprints.reservation import routes