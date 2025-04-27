from apiflask import APIBlueprint

bp = APIBlueprint("hotel", __name__, tag="Hotels")
print("Hotel blueprint initialized:", bp)

from WebApp.blueprints.hotel import routes  # <-- fix import to hotel.routes