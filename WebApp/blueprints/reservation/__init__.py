from apiflask import APIBlueprint

bp = APIBlueprint('reservation', __name__, tag="Reservation")

from WebApp.blueprints.reservation import routes