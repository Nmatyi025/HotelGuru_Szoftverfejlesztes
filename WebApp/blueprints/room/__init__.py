from apiflask import APIBlueprint

bp = APIBlueprint("room", __name__, tag="Rooms")
print("Room blueprint initialized:", bp)

# Import routes to register them with the blueprint
from WebApp.blueprints.room import routes