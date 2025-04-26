from apiflask import APIBlueprint

bp = APIBlueprint("room", __name__, tag="Rooms")
print("Room blueprint initialized:", bp)

from WebApp.blueprints.room import routes