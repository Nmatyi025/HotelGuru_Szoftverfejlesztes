from apiflask import APIBlueprint

bp = APIBlueprint("main", __name__, tag="user")

from WebApp.blueprints.user import routes
